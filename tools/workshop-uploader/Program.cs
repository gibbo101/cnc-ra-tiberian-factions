using System.Reflection;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization;
using Steamworks;

namespace WorkshopUploader;

internal static class Program
{
    private const uint CnCRemasteredAppId = 1213210;

    static Program()
    {
        NativeLibrary.SetDllImportResolver(typeof(SteamAPI).Assembly, (name, asm, path) =>
        {
            if (!name.Equals("steam_api", StringComparison.OrdinalIgnoreCase)) return IntPtr.Zero;
            var baseDir = AppContext.BaseDirectory;
            foreach (var candidate in new[]
                     {
                         Path.Combine(baseDir, "libsteam_api.so"),
                         Path.Combine(baseDir, "runtimes", "linux-x64", "native", "libsteam_api.so"),
                     })
            {
                if (File.Exists(candidate) && NativeLibrary.TryLoad(candidate, out var handle))
                    return handle;
            }
            return IntPtr.Zero;
        });
    }

    private static int Main(string[] args)
    {
        if (args.Length < 2)
        {
            Console.Error.WriteLine("usage: WorkshopUploader <workshop.json> \"<change note>\"");
            return 2;
        }

        var jsonPath = Path.GetFullPath(args[0]);
        var changeNote = args[1];

        if (!File.Exists(jsonPath))
        {
            Console.Error.WriteLine($"workshop.json not found: {jsonPath}");
            return 2;
        }

        WorkshopManifest manifest;
        try
        {
            manifest = JsonSerializer.Deserialize<WorkshopManifest>(
                File.ReadAllText(jsonPath),
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
                ?? throw new InvalidOperationException("manifest deserialised to null");
        }
        catch (Exception e)
        {
            Console.Error.WriteLine($"failed to parse {jsonPath}: {e.Message}");
            return 2;
        }

        if (!manifest.Validate(out var validationError))
        {
            Console.Error.WriteLine($"manifest invalid: {validationError}");
            return 2;
        }

        var contentFolder = ResolvePath(manifest.ContentFolder!, jsonPath);
        var previewFile = string.IsNullOrWhiteSpace(manifest.PreviewFile)
            ? null
            : ResolvePath(manifest.PreviewFile, jsonPath);

        if (!Directory.Exists(contentFolder))
        {
            Console.Error.WriteLine($"content folder does not exist: {contentFolder}");
            return 2;
        }

        long previewBytes = 0;
        if (previewFile != null)
        {
            if (!File.Exists(previewFile))
            {
                Console.Error.WriteLine($"preview file does not exist: {previewFile}");
                return 2;
            }
            previewBytes = new FileInfo(previewFile).Length;
            if (previewBytes >= 1_000_000)
            {
                Console.Error.WriteLine($"preview file too large: {previewBytes} bytes (Steam limit is 1 MB)");
                return 2;
            }
        }

        Console.WriteLine($"item:    {(string.IsNullOrWhiteSpace(manifest.PublishedFileId) ? "<will create new>" : manifest.PublishedFileId)}");
        Console.WriteLine($"title:   {manifest.Title}");
        Console.WriteLine($"tags:    [{string.Join(", ", manifest.Tags ?? new())}]");
        Console.WriteLine($"vis:     {(EVisibility)manifest.Visibility}");
        Console.WriteLine($"content: {contentFolder}");
        Console.WriteLine(previewFile != null
            ? $"preview: {previewFile} ({previewBytes} B)"
            : "preview: <none — keeping existing>");
        Console.WriteLine($"note:    {changeNote}");
        Console.WriteLine();

        if (!SteamAPI.Init())
        {
            Console.Error.WriteLine("SteamAPI.Init() failed. Is Steam running and logged in?");
            Console.Error.WriteLine("(also check steam_appid.txt sits next to the binary with content '1213210')");
            return 1;
        }

        try
        {
            if (string.IsNullOrWhiteSpace(manifest.PublishedFileId))
            {
                Console.WriteLine("no publishedfileid in manifest — creating a new Workshop item shell first...");
                if (!TryCreateItem(out var newId, out var legalAgreementPending)) return 1;
                manifest.PublishedFileId = newId.ToString();
                PersistPublishedFileId(jsonPath, newId);
                Console.WriteLine($"created item {newId}. Persisted to manifest.");
                Console.WriteLine($"  https://steamcommunity.com/sharedfiles/filedetails/?id={newId}");
                if (legalAgreementPending)
                {
                    Console.WriteLine("\nNOTE: Workshop Legal Agreement not yet accepted.");
                    Console.WriteLine("If submit fails, visit the URL above and click 'I Agree' on the banner, then retry.");
                }
                Console.WriteLine();
            }
            return RunUpload(manifest, contentFolder, previewFile, changeNote);
        }
        finally
        {
            SteamAPI.Shutdown();
        }
    }

    private static bool TryCreateItem(out ulong publishedFileId, out bool legalAgreementPending)
    {
        publishedFileId = 0;
        legalAgreementPending = false;

        var fileTypeEnv = Environment.GetEnvironmentVariable("WSU_FILE_TYPE");
        var fileType = EWorkshopFileType.k_EWorkshopFileTypeCommunity;
        if (!string.IsNullOrWhiteSpace(fileTypeEnv) && Enum.TryParse<EWorkshopFileType>(fileTypeEnv, true, out var parsed))
        {
            fileType = parsed;
        }
        Console.WriteLine($"  CreateItem fileType: {fileType}");

        var apiCall = SteamUGC.CreateItem(new AppId_t(CnCRemasteredAppId), fileType);

        var done = false;
        var resultCode = EResult.k_EResultFail;
        ulong newId = 0;
        var legal = false;

        var callResult = CallResult<CreateItemResult_t>.Create((result, ioFailure) =>
        {
            if (ioFailure)
            {
                Console.Error.WriteLine("CreateItem: IO failure");
                resultCode = EResult.k_EResultIOFailure;
            }
            else
            {
                resultCode = result.m_eResult;
                newId = result.m_nPublishedFileId.m_PublishedFileId;
                legal = result.m_bUserNeedsToAcceptWorkshopLegalAgreement;
            }
            done = true;
        });
        callResult.Set(apiCall);

        var deadline = DateTime.UtcNow.AddSeconds(30);
        while (!done && DateTime.UtcNow < deadline)
        {
            SteamAPI.RunCallbacks();
            Thread.Sleep(100);
        }

        if (!done)
        {
            Console.Error.WriteLine("CreateItem: no callback within 30s. Steam may be unreachable.");
            return false;
        }
        if (resultCode != EResult.k_EResultOK)
        {
            Console.Error.WriteLine($"CreateItem FAILED — EResult.{resultCode} ({(int)resultCode})");
            return false;
        }

        publishedFileId = newId;
        legalAgreementPending = legal;
        return true;
    }

    private static void PersistPublishedFileId(string jsonPath, ulong publishedFileId)
    {
        var text = File.ReadAllText(jsonPath);
        var doc = JsonNode.Parse(text)!.AsObject();
        doc["publishedfileid"] = publishedFileId.ToString();
        File.WriteAllText(jsonPath, doc.ToJsonString(new JsonSerializerOptions { WriteIndented = true }));
    }

    private static int RunUpload(WorkshopManifest manifest, string contentFolder, string? previewFile, string changeNote)
    {
        var publishedFileId = new PublishedFileId_t(ulong.Parse(manifest.PublishedFileId!));
        var appId = new AppId_t(CnCRemasteredAppId);

        var handle = SteamUGC.StartItemUpdate(appId, publishedFileId);

        if (!SteamUGC.SetItemContent(handle, contentFolder)) return Fail("SetItemContent");
        if (previewFile != null && !SteamUGC.SetItemPreview(handle, previewFile)) return Fail("SetItemPreview");
        if (!SteamUGC.SetItemUpdateLanguage(handle, "English")) return Fail("SetItemUpdateLanguage");
        if (!SteamUGC.SetItemTitle(handle, manifest.Title!)) return Fail("SetItemTitle");
        if (!SteamUGC.SetItemDescription(handle, manifest.Description ?? "")) return Fail("SetItemDescription");
        if (!SteamUGC.SetItemVisibility(handle, (ERemoteStoragePublishedFileVisibility)manifest.Visibility)) return Fail("SetItemVisibility");
        if (manifest.Tags is { Count: > 0 } && !SteamUGC.SetItemTags(handle, manifest.Tags)) return Fail("SetItemTags");

        Console.WriteLine("submitting update...");
        var apiCall = SteamUGC.SubmitItemUpdate(handle, changeNote);

        var done = false;
        var resultCode = EResult.k_EResultFail;
        var userNeedsToAcceptWorkshopLegalAgreement = false;

        var callResult = CallResult<SubmitItemUpdateResult_t>.Create((result, ioFailure) =>
        {
            if (ioFailure)
            {
                Console.Error.WriteLine("SubmitItemUpdate: IO failure during call");
                resultCode = EResult.k_EResultIOFailure;
            }
            else
            {
                resultCode = result.m_eResult;
                userNeedsToAcceptWorkshopLegalAgreement = result.m_bUserNeedsToAcceptWorkshopLegalAgreement;
            }
            done = true;
        });
        callResult.Set(apiCall);

        var lastStatus = EItemUpdateStatus.k_EItemUpdateStatusInvalid;
        ulong lastProcessed = 0;
        var started = DateTime.UtcNow;

        while (!done)
        {
            SteamAPI.RunCallbacks();
            var status = SteamUGC.GetItemUpdateProgress(handle, out var processed, out var total);
            if (status != lastStatus || processed != lastProcessed)
            {
                lastStatus = status;
                lastProcessed = processed;
                var pct = total > 0 ? $"{processed * 100 / total}%" : "—";
                var hr = total > 0 ? $"{HumanBytes(processed)}/{HumanBytes(total)}" : "";
                Console.WriteLine($"  [{(DateTime.UtcNow - started).TotalSeconds,5:F0}s] {StatusLabel(status),-22} {pct,5} {hr}");
            }
            Thread.Sleep(250);
        }

        if (resultCode == EResult.k_EResultOK)
        {
            Console.WriteLine($"\nSUCCESS — item {publishedFileId.m_PublishedFileId} updated.");
            Console.WriteLine($"  https://steamcommunity.com/sharedfiles/filedetails/?id={publishedFileId.m_PublishedFileId}");
            if (userNeedsToAcceptWorkshopLegalAgreement)
            {
                Console.WriteLine("\nNOTE: Steam reports you still need to accept the Workshop Legal Agreement.");
                Console.WriteLine("Visit the item page above and click 'I Agree' on the banner, otherwise the item stays hidden.");
            }
            return 0;
        }

        Console.Error.WriteLine($"\nFAILED — EResult.{resultCode} ({(int)resultCode})");
        if (userNeedsToAcceptWorkshopLegalAgreement)
        {
            Console.Error.WriteLine("Steam reports you need to accept the Workshop Legal Agreement first.");
            Console.Error.WriteLine($"Visit https://steamcommunity.com/sharedfiles/filedetails/?id={publishedFileId.m_PublishedFileId} and accept.");
        }
        return 1;
    }

    private static int Fail(string step)
    {
        Console.Error.WriteLine($"SteamUGC.{step} returned false");
        return 1;
    }

    private static string ResolvePath(string raw, string jsonPath)
    {
        var normalised = raw.Replace('\\', Path.DirectorySeparatorChar);
        return Path.IsPathRooted(normalised)
            ? Path.GetFullPath(normalised)
            : Path.GetFullPath(Path.Combine(Path.GetDirectoryName(jsonPath)!, normalised));
    }

    private static string StatusLabel(EItemUpdateStatus s) => s switch
    {
        EItemUpdateStatus.k_EItemUpdateStatusInvalid              => "invalid",
        EItemUpdateStatus.k_EItemUpdateStatusPreparingConfig      => "preparing config",
        EItemUpdateStatus.k_EItemUpdateStatusPreparingContent     => "preparing content",
        EItemUpdateStatus.k_EItemUpdateStatusUploadingContent     => "uploading content",
        EItemUpdateStatus.k_EItemUpdateStatusUploadingPreviewFile => "uploading preview",
        EItemUpdateStatus.k_EItemUpdateStatusCommittingChanges    => "committing",
        _ => s.ToString(),
    };

    private static string HumanBytes(ulong b)
    {
        if (b < 1024) return $"{b} B";
        if (b < 1024 * 1024) return $"{b / 1024.0:F1} KB";
        if (b < 1024UL * 1024 * 1024) return $"{b / (1024.0 * 1024):F1} MB";
        return $"{b / (1024.0 * 1024 * 1024):F2} GB";
    }

    private enum EVisibility { Public = 0, FriendsOnly = 1, Private = 2, Unlisted = 3 }
}

internal sealed class WorkshopManifest
{
    [JsonPropertyName("publishedfileid")] public string? PublishedFileId { get; set; }
    [JsonPropertyName("contentfolder")]   public string? ContentFolder { get; set; }
    [JsonPropertyName("previewfile")]     public string? PreviewFile { get; set; }
    [JsonPropertyName("visibility")]      public int Visibility { get; set; }
    [JsonPropertyName("title")]           public string? Title { get; set; }
    [JsonPropertyName("description")]     public string? Description { get; set; }
    [JsonPropertyName("tags")]            public List<string>? Tags { get; set; }
    [JsonPropertyName("metadata")]        public string? Metadata { get; set; }

    public bool Validate(out string error)
    {
        if (!string.IsNullOrWhiteSpace(PublishedFileId) && !ulong.TryParse(PublishedFileId, out _))
        { error = "publishedfileid present but not a number"; return false; }
        if (string.IsNullOrWhiteSpace(ContentFolder)) { error = "contentfolder missing"; return false; }
        if (string.IsNullOrWhiteSpace(Title))         { error = "title missing"; return false; }
        if (Visibility is < 0 or > 3)                 { error = "visibility must be 0..3"; return false; }
        error = "";
        return true;
    }
}
