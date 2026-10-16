/*
**	The encyclopedia's pictures, drawn from the game's own sprite art (docs/encyclopedia.md): the tileset XMLs name
**	each art's frames, held in ZIPs (or, for theatre art, loose DDS) in the mod, the asset packs or the game's MEGs.
*/
#include "function.h"
#include "tf_encyclopedia.h"

extern "C" {
#include "puff.h"
}

#include <cmath>
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <vector>

namespace {

const double HD_PER_CLASSIC = 128.0 / 24.0;
const int MARGIN = 10;
const double MAX_SCALE = 2.5;
const int INFANTRY_FACING = 3; // of the 8 standing frames: south-west
const int FACING = 12;         // of 32: south-west
const int MAX_SIDE = 2048;               // the largest frame side read from a file; a canvas is twice that
const unsigned long MAX_MEMBER = 64u << 20; // the largest ZIP member unpacked

// Trap: the game's own min and max (jshell.h) take ints, so floats would be truncated through them.
template <class T> T Lo(T a, T b)
{
    return a < b ? a : b;
}

template <class T> T Hi(T a, T b)
{
    return a > b ? a : b;
}

// True for a width and height a frame can have; files claiming more are malformed.
bool Sane_Size(int w, int h)
{
    return w > 0 && h > 0 && w <= MAX_SIDE && h <= MAX_SIDE;
}

struct Image
{
    int Width;
    int Height;
    std::vector<unsigned char> Pixels; // RGBA, straight alpha

    Image(int w = 0, int h = 0)
        : Width(w)
        , Height(h)
        , Pixels((size_t)w * h * 4, 0)
    {
    }
    unsigned char* At(int x, int y)
    {
        return &Pixels[((size_t)y * Width + x) * 4];
    }
};

struct Tile
{
    std::string Root;                 // the tileset's RootTexturePath
    std::map<int, std::string> Frame; // shape -> its first frame's path
};

// A team colour as CONFIG.MEG's team colour XMLs give it: hue bounds as 0-1 RGB, fudge and the HSV shift.
struct Team
{
    float Lower[3];
    float Upper[3];
    float Fudge;
    float Shift[3];
};

const Team TEAMS[] = {
    {{0.264706f, 1, 0}, {0, 1, 0.22f}, 0, {0.310f, -0.211f, 0.005f}}, // GREECE
    {{0.264706f, 1, 0}, {0, 1, 0.22f}, 0, {0.689f, 0.382f, 0}},       // USSR
    {{0.26f, 1, 0}, {0, 1, 0.22f}, 0, {0.777f, -0.196f, 0}},          // TD GOOD
    {{0.26f, 1, 0}, {0, 1, 0.22f}, 0, {0.306f, -0.655f, 0}},          // TD BAD_UNIT
    {{0.264706f, 1, 0}, {0, 1, 0.22f}, 0, {0.667f, 0.185f, 0}},       // TD BAD_STRUCTURE
};

std::map<std::string, Tile> Tiles;
bool TilesRead = false;
struct MegMember
{
    int Meg;
    unsigned Offset;
    unsigned Size;
};

// The game's MEGs the art and its tilesets come from; a member in more than one is read from the first.
const char* const MEGS[] = {"TEXTURES_RA_SRGB.MEG", "TEXTURES_COMMON_SRGB.MEG", "CONFIG.MEG"};
std::map<std::string, MegMember> MegIndex;
std::string MegPaths[sizeof(MEGS) / sizeof(MEGS[0])];
bool MegRead = false;

std::string Upper(std::string text)
{
    for (size_t i = 0; i < text.size(); i++) {
        text[i] = (char)toupper((unsigned char)text[i]);
    }
    return text;
}

bool Read_File(const std::string& path, std::vector<unsigned char>& out)
{
    FILE* f = fopen(path.c_str(), "rb");
    if (f == NULL) {
        return false;
    }
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    out.resize(size > 0 ? (size_t)size : 0);
    bool ok = size > 0 && fread(&out[0], 1, (size_t)size, f) == (size_t)size;
    fclose(f);
    return ok;
}

/*
**	The text between `open` and `close` from `at` on in `text`, moving `at` past it; false when there is none.
*/
bool Next_Tag(const std::string& text, size_t& at, const char* open, const char* close, std::string& out)
{
    size_t a = text.find(open, at);
    if (a == std::string::npos) {
        return false;
    }
    a += strlen(open);
    size_t b = text.find(close, a);
    if (b == std::string::npos) {
        return false;
    }
    out = text.substr(a, b - a);
    at = b + strlen(close);
    return true;
}

void Read_Tileset(const std::vector<unsigned char>& bytes)
{
    std::string text(bytes.begin(), bytes.end());
    size_t at = 0;
    std::string root;
    while (Next_Tag(text, at, "<RootTexturePath>", "</RootTexturePath>", root)) {
        size_t end = text.find("</TilesetTypeClass>", at);
        std::string block = text.substr(at, end == std::string::npos ? std::string::npos : end - at);
        size_t b = 0;
        std::string name, shape, frame;
        while (Next_Tag(block, b, "<Name>", "</Name>", name)) {
            size_t s = block.find_first_not_of(" \t\r\n", b);
            if (s == std::string::npos || block.compare(s, 7, "<Shape>") != 0
                || !Next_Tag(block, s, "<Shape>", "</Shape>", shape)) {
                continue;
            }
            size_t f = s;
            if (!Next_Tag(block, f, "<Frame>", "</Frame>", frame)) {
                break;
            }
            Tile& tile = Tiles[Upper(name)];
            if (tile.Root.empty()) {
                tile.Root = root;
            }
            if (tile.Frame.find(atoi(shape.c_str())) == tile.Frame.end()) {
                tile.Frame[atoi(shape.c_str())] = frame;
            }
            b = s;
        }
        if (end == std::string::npos) {
            break;
        }
        at = end;
    }
}

/*
**	Indexes the game's MEGs once (layout: scripts/meg_extract.py).
*/
void Read_Megs(void)
{
    MegRead = true;
    char exe[MAX_PATH];
    if (GetModuleFileNameA(NULL, exe, sizeof(exe)) == 0) {
        return;
    }
    char* slash = strrchr(exe, '\\');
    if (slash == NULL) {
        return;
    }
    *slash = 0;
    for (int m = 0; m < (int)(sizeof(MEGS) / sizeof(MEGS[0])); m++) {
        MegPaths[m] = std::string(exe) + "\\Data\\" + MEGS[m];
        FILE* f = fopen(MegPaths[m].c_str(), "rb");
        if (f == NULL) {
            continue;
        }
        unsigned head[2] = {0, 0};
        unsigned counts[3];
        if (fread(head, 4, 2, f) == 2
            && fseek(f, (head[0] == 0xFFFFFFFF || head[0] == 0x8FFFFFFF) ? 12 : 4, SEEK_SET) == 0
            && fread(counts, 4, 3, f) == 3 && counts[2] < (64u << 20) && counts[0] < 1000000) {
            std::vector<unsigned char> table(counts[2] + (size_t)counts[0] * 20);
            if (fread(&table[0], 1, table.size(), f) == table.size()) {
                std::vector<std::string> strings;
                size_t at = 0;
                for (unsigned i = 0; i < counts[1] && at + 2 <= counts[2]; i++) {
                    unsigned short length = *(unsigned short*)&table[at];
                    if (at + 2 + length > counts[2]) {
                        break;
                    }
                    strings.push_back(Upper(std::string((const char*)&table[at + 2], length)));
                    at += 2 + length;
                }
                for (unsigned i = 0; i < counts[0]; i++) {
                    const unsigned char* record = &table[counts[2] + (size_t)i * 20];
                    unsigned short name = *(const unsigned short*)(record + 18);
                    if (name < strings.size() && MegIndex.find(strings[name]) == MegIndex.end()) {
                        MegMember member = {m, *(const unsigned*)(record + 14), *(const unsigned*)(record + 10)};
                        MegIndex[strings[name]] = member;
                    }
                }
            }
        }
        fclose(f);
    }
}

bool Read_Meg_Member(const std::string& name, std::vector<unsigned char>& out)
{
    if (!MegRead) {
        Read_Megs();
    }
    std::map<std::string, MegMember>::const_iterator it = MegIndex.find(Upper(name));
    if (it == MegIndex.end()) {
        return false;
    }
    FILE* f = fopen(MegPaths[it->second.Meg].c_str(), "rb");
    if (f == NULL) {
        return false;
    }
    out.resize(it->second.Size);
    bool ok = out.empty()
              || (_fseeki64(f, (long long)it->second.Offset, SEEK_SET) == 0
                  && fread(&out[0], 1, out.size(), f) == out.size());
    fclose(f);
    return ok;
}

/*
**	Every tileset XML of the mod and the asset packs, then the game's own RA and common ones from CONFIG.MEG for
**	art the mod doesn't name (the rotors); temperate theatre first so its art wins.
*/
void Read_Tilesets(void)
{
    TilesRead = true;
    std::vector<std::string> first, last, stock_first, stock_last;
    for (int i = 0; TF_Encyclopedia_Root(i) != NULL; i++) {
        std::string folder = std::string(TF_Encyclopedia_Root(i)) + "\\Data\\XML\\TILESETS\\";
        WIN32_FIND_DATAA found;
        HANDLE find = FindFirstFileA((folder + "*.XML").c_str(), &found);
        if (find == INVALID_HANDLE_VALUE) {
            continue;
        }
        do {
            std::string name = Upper(found.cFileName);
            bool other = name.find("SNOW") != std::string::npos || name.find("INTERIOR") != std::string::npos;
            (other ? last : first).push_back(folder + found.cFileName);
        } while (FindNextFileA(find, &found));
        FindClose(find);
    }
    if (!MegRead) {
        Read_Megs();
    }
    const std::string stock = "DATA\\XML\\TILESETS\\";
    for (std::map<std::string, MegMember>::const_iterator it = MegIndex.begin(); it != MegIndex.end(); ++it) {
        if (it->first.compare(0, stock.size(), stock) == 0
            && (it->first.compare(stock.size(), 3, "RA_") == 0 || it->first.compare(stock.size(), 7, "COMMON_") == 0)) {
            bool other = it->first.find("SNOW") != std::string::npos || it->first.find("INTERIOR") != std::string::npos;
            (other ? stock_last : stock_first).push_back(it->first);
        }
    }
    std::vector<unsigned char> bytes;
    for (size_t i = 0; i < first.size(); i++) {
        if (Read_File(first[i], bytes)) {
            Read_Tileset(bytes);
        }
    }
    for (size_t i = 0; i < stock_first.size(); i++) {
        if (Read_Meg_Member(stock_first[i], bytes)) {
            Read_Tileset(bytes);
        }
    }
    for (size_t i = 0; i < last.size(); i++) {
        if (Read_File(last[i], bytes)) {
            Read_Tileset(bytes);
        }
    }
    for (size_t i = 0; i < stock_last.size(); i++) {
        if (Read_Meg_Member(stock_last[i], bytes)) {
            Read_Tileset(bytes);
        }
    }
}


/*
**	One archive member's bytes from a ZIP held in memory, matched case-insensitively; false when absent.
*/
bool Zip_Member(const std::vector<unsigned char>& zip, const std::string& name, std::vector<unsigned char>& out)
{
    size_t n = zip.size();
    if (n < 22) {
        return false;
    }
    size_t eocd = n - 22;
    while (eocd > 0 && *(const unsigned*)&zip[eocd] != 0x06054b50) {
        eocd--;
    }
    if (*(const unsigned*)&zip[eocd] != 0x06054b50) {
        return false;
    }
    unsigned count = *(const unsigned short*)&zip[eocd + 10];
    size_t at = *(const unsigned*)&zip[eocd + 16];
    std::string wanted = Upper(name);
    for (unsigned i = 0; i < count && at + 46 <= n; i++) {
        if (*(const unsigned*)&zip[at] != 0x02014b50) {
            return false;
        }
        unsigned method = *(const unsigned short*)&zip[at + 10];
        unsigned long packed = *(const unsigned*)&zip[at + 20];
        unsigned long size = *(const unsigned*)&zip[at + 24];
        size_t name_length = *(const unsigned short*)&zip[at + 28];
        size_t skip = name_length + *(const unsigned short*)&zip[at + 30] + *(const unsigned short*)&zip[at + 32];
        size_t local = *(const unsigned*)&zip[at + 42];
        if (at + 46 + name_length > n) {
            return false;
        }
        std::string member((const char*)&zip[at + 46], name_length);
        at += 46 + skip;
        if (Upper(member) != wanted || local + 30 > n) {
            continue;
        }
        size_t data = local + 30 + *(const unsigned short*)&zip[local + 26] + *(const unsigned short*)&zip[local + 28];
        if (data + packed > n || size > MAX_MEMBER || (method == 0 && size > packed)) {
            return false;
        }
        out.resize(size);
        if (method == 0) {
            memcpy(out.empty() ? NULL : &out[0], &zip[data], size);
            return true;
        }
        unsigned long length = size;
        unsigned long source = packed;
        return method == 8 && puff(out.empty() ? NULL : &out[0], &length, &zip[data], &source) == 0;
    }
    return false;
}

/*
**	A frame's ZIP: the asset packs' or the mod's loose copy, else the game's MEG; cached for the next frame.
*/
const std::vector<unsigned char>* Zip_For(const std::string& root, const std::string& folder)
{
    static std::string cached_key;
    static std::vector<unsigned char> cached;
    std::string rel = "ART\\TEXTURES\\SRGB\\" + Upper(root) + "\\" + Upper(folder) + ".ZIP";
    if (rel == cached_key) {
        return cached.empty() ? NULL : &cached;
    }
    cached_key = rel;
    cached.clear();
    for (int i = 0; TF_Encyclopedia_Root(i) != NULL; i++) {
        if (Read_File(std::string(TF_Encyclopedia_Root(i)) + "\\Data\\" + rel, cached)) {
            return &cached;
        }
    }
    if (Read_Meg_Member("DATA\\" + rel, cached)) {
        return &cached;
    }
    cached.clear();
    return NULL;
}

/*
**	A TGA's pixels (uncompressed or RLE, 24 or 32 bit) as RGBA; false for anything else.
*/
bool Decode_Tga(const std::vector<unsigned char>& tga, Image& out)
{
    if (tga.size() < 18 || (tga[2] != 2 && tga[2] != 10) || (tga[16] != 32 && tga[16] != 24)) {
        return false;
    }
    int w = tga[12] | (tga[13] << 8);
    int h = tga[14] | (tga[15] << 8);
    if (!Sane_Size(w, h)) {
        return false;
    }
    int bytes = tga[16] / 8;
    bool top_down = (tga[17] & 0x20) != 0;
    out = Image(w, h);
    size_t at = 18 + tga[0];
    size_t total = (size_t)w * h;
    size_t pixel = 0;
    while (pixel < total) {
        int run = 1;
        bool repeat = false;
        if (tga[2] == 10) {
            if (at >= tga.size()) {
                return false;
            }
            repeat = (tga[at] & 0x80) != 0;
            run = (tga[at] & 0x7F) + 1;
            at++;
        }
        for (int i = 0; i < run && pixel < total; i++, pixel++) {
            if (at + bytes > tga.size()) {
                return false;
            }
            int x = (int)(pixel % w);
            int y = (int)(pixel / w);
            unsigned char* p = out.At(x, top_down ? y : h - 1 - y);
            p[0] = tga[at + 2];
            p[1] = tga[at + 1];
            p[2] = tga[at];
            p[3] = bytes == 4 ? tga[at + 3] : 255;
            if (tga[2] == 2 || !repeat || i == run - 1) {
                at += bytes;
            }
        }
    }
    return true;
}

/*
**	A DDS's top level as RGBA: DXT1, DXT5 or uncompressed 32-bit; false for anything else.
*/
bool Decode_Dds(const std::vector<unsigned char>& dds, Image& out)
{
    if (dds.size() < 128 || memcmp(&dds[0], "DDS ", 4) != 0) {
        return false;
    }
    int h = *(const int*)&dds[12];
    int w = *(const int*)&dds[16];
    if (!Sane_Size(w, h)) {
        return false;
    }
    unsigned flags = *(const unsigned*)&dds[80];
    std::string fourcc((const char*)&dds[84], 4);
    out = Image(w, h);
    const unsigned char* data = &dds[128];
    size_t left = dds.size() - 128;
    if ((flags & 0x4) == 0) {
        if (*(const unsigned*)&dds[88] != 32 || left < (size_t)w * h * 4) {
            return false;
        }
        unsigned rmask = *(const unsigned*)&dds[92];
        for (int i = 0; i < w * h; i++) {
            const unsigned char* p = data + (size_t)i * 4;
            unsigned char* d = &out.Pixels[(size_t)i * 4];
            bool bgr = rmask == 0x00FF0000;
            d[0] = bgr ? p[2] : p[0];
            d[1] = p[1];
            d[2] = bgr ? p[0] : p[2];
            d[3] = p[3];
        }
        return true;
    }
    bool dxt5 = fourcc == "DXT5";
    if (!dxt5 && fourcc != "DXT1") {
        return false;
    }
    size_t block_bytes = dxt5 ? 16 : 8;
    if (left < (size_t)((w + 3) / 4) * ((h + 3) / 4) * block_bytes) {
        return false;
    }
    for (int by = 0; by < (h + 3) / 4; by++) {
        for (int bx = 0; bx < (w + 3) / 4; bx++) {
            const unsigned char* block = data + ((size_t)by * ((w + 3) / 4) + bx) * block_bytes;
            unsigned char alpha[16];
            for (int i = 0; i < 16; i++) {
                alpha[i] = 255;
            }
            if (dxt5) {
                int a0 = block[0], a1 = block[1];
                unsigned long long bits = 0;
                for (int i = 0; i < 6; i++) {
                    bits |= (unsigned long long)block[2 + i] << (8 * i);
                }
                for (int i = 0; i < 16; i++) {
                    int code = (int)((bits >> (3 * i)) & 7);
                    int a = code == 0   ? a0
                            : code == 1 ? a1
                            : a0 > a1   ? ((8 - code) * a0 + (code - 1) * a1) / 7
                            : code == 6 ? 0
                            : code == 7 ? 255
                                        : ((6 - code) * a0 + (code - 1) * a1) / 5;
                    alpha[i] = (unsigned char)a;
                }
                block += 8;
            }
            unsigned c0 = block[0] | (block[1] << 8), c1 = block[2] | (block[3] << 8);
            int colour[4][4];
            for (int k = 0; k < 2; k++) {
                unsigned c = k ? c1 : c0;
                colour[k][0] = ((c >> 11) & 31) * 255 / 31;
                colour[k][1] = ((c >> 5) & 63) * 255 / 63;
                colour[k][2] = (c & 31) * 255 / 31;
                colour[k][3] = 255;
            }
            bool four = dxt5 || c0 > c1;
            for (int ch = 0; ch < 3; ch++) {
                colour[2][ch] = four ? (2 * colour[0][ch] + colour[1][ch]) / 3 : (colour[0][ch] + colour[1][ch]) / 2;
                colour[3][ch] = four ? (colour[0][ch] + 2 * colour[1][ch]) / 3 : 0;
            }
            colour[2][3] = 255;
            colour[3][3] = four ? 255 : 0;
            unsigned indices = block[4] | (block[5] << 8) | (block[6] << 16) | ((unsigned)block[7] << 24);
            for (int i = 0; i < 16; i++) {
                int x = bx * 4 + i % 4, y = by * 4 + i / 4;
                if (x < w && y < h) {
                    const int* c = colour[(indices >> (2 * i)) & 3];
                    unsigned char* d = out.At(x, y);
                    d[0] = (unsigned char)c[0];
                    d[1] = (unsigned char)c[1];
                    d[2] = (unsigned char)c[2];
                    d[3] = dxt5 ? alpha[i] : (unsigned char)c[3];
                }
            }
        }
    }
    return true;
}

/*
**	A theatre frame stored as a loose DDS (MSLO.TEM\MSLO.TEM-0000.DDS): the asset packs' or the mod's, else the MEG's.
*/
bool Loose_Frame(const std::string& root, const std::string& folder, const std::string& file, Image& out)
{
    std::string rel = "ART\\TEXTURES\\SRGB\\" + Upper(root) + "\\" + Upper(folder) + "\\"
                      + Upper(file.substr(0, file.size() - 4)) + ".DDS";
    std::vector<unsigned char> dds;
    bool found = false;
    for (int i = 0; !found && TF_Encyclopedia_Root(i) != NULL; i++) {
        found = Read_File(std::string(TF_Encyclopedia_Root(i)) + "\\Data\\" + rel, dds);
    }
    return (found || Read_Meg_Member("DATA\\" + rel, dds)) && Decode_Dds(dds, out);
}

/*
**	The two numbers after `"key"` in a frame's .meta JSON.
*/
bool Meta_Pair(const std::string& meta, const char* key, int& a, int& b)
{
    size_t at = meta.find(std::string("\"") + key + "\"");
    if (at == std::string::npos || (at = meta.find('[', at)) == std::string::npos) {
        return false;
    }
    return sscanf(meta.c_str() + at, "[%d ,%d", &a, &b) == 2 || sscanf(meta.c_str() + at, "[%d,%d", &a, &b) == 2;
}

/*
**	One frame on its full canvas, from a tileset frame path like 'dd\dd-0000-0000.tga'; false when unreadable.
*/
bool Read_Frame(const Tile& tile, int shape, Image& out)
{
    std::map<int, std::string>::const_iterator it = tile.Frame.find(shape);
    if (it == tile.Frame.end()) {
        return false;
    }
    std::string path = it->second;
    size_t slash = path.find_last_of("\\/");
    if (slash == std::string::npos) {
        return false;
    }
    std::string file = path.substr(slash + 1);
    std::string folder = path.substr(0, slash);
    size_t up = folder.find_last_of("\\/");
    if (up != std::string::npos) {
        folder = folder.substr(up + 1);
    }
    const std::vector<unsigned char>* zip = Zip_For(tile.Root, folder);
    std::vector<unsigned char> tga, meta;
    if (zip == NULL || !Zip_Member(*zip, file, tga)) {
        return Loose_Frame(tile.Root, folder, file, out);
    }
    Image sprite;
    if (!Decode_Tga(tga, sprite)) {
        return false;
    }
    int w, h, x, y;
    std::string meta_name = file.substr(0, file.size() - 4) + ".meta";
    if (!Zip_Member(*zip, meta_name, meta)) {
        out = sprite;
        return true;
    }
    std::string text(meta.begin(), meta.end());
    if (!Meta_Pair(text, "size", w, h) || !Meta_Pair(text, "crop", x, y) || !Sane_Size(w, h)) {
        out = sprite;
        return true;
    }
    out = Image(w, h);
    for (int sy = 0; sy < sprite.Height; sy++) {
        for (int sx = 0; sx < sprite.Width; sx++) {
            if (sx + x >= 0 && sx + x < w && sy + y >= 0 && sy + y < h) {
                memcpy(out.At(sx + x, sy + y), sprite.At(sx, sy), 4);
            }
        }
    }
    return true;
}

/*
**	Draws `top` over `base` with its top-left at `x`, `y` (straight alpha over).
*/
void Composite(Image& base, Image& top, int x, int y)
{
    for (int ty = 0; ty < top.Height; ty++) {
        for (int tx = 0; tx < top.Width; tx++) {
            int bx = tx + x, by = ty + y;
            if (bx < 0 || by < 0 || bx >= base.Width || by >= base.Height) {
                continue;
            }
            unsigned char* s = top.At(tx, ty);
            unsigned char* d = base.At(bx, by);
            float sa = s[3] / 255.0f, da = d[3] / 255.0f;
            float oa = sa + da * (1 - sa);
            for (int c = 0; c < 3 && oa > 0; c++) {
                d[c] = (unsigned char)((s[c] * sa + d[c] * da * (1 - sa)) / oa + 0.5f);
            }
            d[3] = (unsigned char)(oa * 255 + 0.5f);
        }
    }
}

/*
**	Keeps only the pixels joined to the sprite's middle through solid ones, and the soft edge around them: a
**	build-up frame's last flecks of dust go.
*/
void Drop_Specks(Image& img)
{
    int w = img.Width, h = img.Height;
    std::vector<unsigned char> keep((size_t)w * h, 0);
    long sx = 0, sy = 0, count = 0;
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            if (img.At(x, y)[3] > 96) {
                sx += x;
                sy += y;
                count++;
            }
        }
    }
    if (count == 0) {
        return;
    }
    double mx = (double)sx / count, my = (double)sy / count, best = 1e30;
    int seed = -1;
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            double d = (x - mx) * (x - mx) + (y - my) * (y - my);
            if (img.At(x, y)[3] > 96 && d < best) {
                best = d;
                seed = y * w + x;
            }
        }
    }
    std::vector<int> stack(1, seed);
    keep[seed] = 1;
    while (!stack.empty()) {
        int p = stack.back();
        stack.pop_back();
        int px = p % w, py = p / w;
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                int nx = px + dx, ny = py + dy;
                if (nx >= 0 && ny >= 0 && nx < w && ny < h && !keep[ny * w + nx] && img.At(nx, ny)[3] > 96) {
                    keep[ny * w + nx] = 1;
                    stack.push_back(ny * w + nx);
                }
            }
        }
    }
    for (int pass = 0; pass < 3; pass++) {
        std::vector<unsigned char> grown = keep;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                if (keep[y * w + x]) {
                    for (int dy = -1; dy <= 1; dy++) {
                        for (int dx = -1; dx <= 1; dx++) {
                            int nx = x + dx, ny = y + dy;
                            if (nx >= 0 && ny >= 0 && nx < w && ny < h && img.At(nx, ny)[3] > 0) {
                                grown[ny * w + nx] = 1;
                            }
                        }
                    }
                }
            }
        }
        keep.swap(grown);
    }
    for (int i = 0; i < w * h; i++) {
        if (!keep[i]) {
            img.Pixels[(size_t)i * 4 + 3] = 0;
        }
    }
}

float To_Linear(float c)
{
    return c <= 0.04045f ? c / 12.92f : powf((c + 0.055f) / 1.055f, 2.4f);
}

float To_Srgb(float c)
{
    return c <= 0.0031308f ? c * 12.92f : 1.055f * powf(c, 1 / 2.4f) - 0.055f;
}

/*
**	A team colour bound's hue as the client reads it: the 0-1 RGB truncated to bytes, then GDI+'s GetHue.
*/
float Bound_Hue(const float* rgb)
{
    float r = (int)(rgb[0] * 255) / 255.0f, g = (int)(rgb[1] * 255) / 255.0f, b = (int)(rgb[2] * 255) / 255.0f;
    float high = Hi(r, Hi(g, b)), low = Lo(r, Lo(g, b));
    if (high == low) {
        return 0;
    }
    float h = high == r ? (g - b) / (high - low) : high == g ? 2 + (b - r) / (high - low) : 4 + (r - g) / (high - low);
    h *= 60;
    if (h < 0) {
        h += 360;
    }
    return h / 360;
}

float Fraction(float x)
{
    return x - (int)x;
}

/*
**	Recolours house-colour green as the client's team colour does (TextureManager.cs in the game's SOURCECODE
**	map editor): in linear light, a hue between the bounds is shifted by the house's HSV shift.
*/
void House_Colour(Image& img, const Team& team)
{
    float lower = Bound_Hue(team.Lower), upper = Bound_Hue(team.Upper);
    for (int i = 0; i < img.Width * img.Height; i++) {
        unsigned char* p = &img.Pixels[(size_t)i * 4];
        if (p[3] == 0) {
            continue;
        }
        float r = To_Linear(p[0] / 255.0f), g = To_Linear(p[1] / 255.0f), b = To_Linear(p[2] / 255.0f);
        float px, py, pz, pw;
        if (g >= b) {
            px = g, py = b, pz = 0, pw = -1.0f / 3;
        } else {
            px = b, py = g, pz = -1, pw = 2.0f / 3;
        }
        float qx, qy = py, qz, qw;
        if (r >= px) {
            qx = r, qz = pz, qw = px;
        } else {
            qx = px, qz = pw, qw = r;
        }
        float d = qx - Lo(qw, qy);
        float hue = fabsf(qz + (qw - qy) / (6 * d + 1e-10f));
        if (hue < lower || hue > upper) {
            continue;
        }
        float sat = d / (qx + 1e-10f), value = qx;
        hue = hue / (upper - lower) * ((upper + team.Fudge) - (lower - team.Fudge)) + team.Shift[0];
        sat += team.Shift[1];
        value += team.Shift[2];
        static const float k[3] = {1.0f, 2.0f / 3, 1.0f / 3};
        for (int c = 0; c < 3; c++) {
            float m = fabsf(Fraction(hue + k[c]) * 6 - 3);
            float lit = value * (1 + (Lo(Hi(m - 1, 0.0f), 1.0f) - 1) * sat);
            p[c] = (unsigned char)(Lo(Hi(To_Srgb(Lo(Hi(lit, 0.0f), 1.0f)), 0.0f), 1.0f) * 255);
        }
    }
}

/*
**	The sprite cropped to its pixels and fitted to `rgba` with a margin, centred; area-averaged in premultiplied
**	alpha so edges keep their colour.
*/
void Fit(Image& img, unsigned char* rgba, int width, int height)
{
    memset(rgba, 0, (size_t)width * height * 4);
    int x0 = img.Width, y0 = img.Height, x1 = -1, y1 = -1;
    for (int y = 0; y < img.Height; y++) {
        for (int x = 0; x < img.Width; x++) {
            if (img.At(x, y)[3] > 0) {
                x0 = Lo(x0, x), y0 = Lo(y0, y), x1 = Hi(x1, x), y1 = Hi(y1, y);
            }
        }
    }
    if (x1 < 0) {
        return;
    }
    int w = x1 - x0 + 1, h = y1 - y0 + 1;
    double scale = Lo(Lo((double)(width - 2 * MARGIN) / w, (double)(height - 2 * MARGIN) / h), MAX_SCALE);
    int ow = Hi(1, (int)(w * scale + 0.5)), oh = Hi(1, (int)(h * scale + 0.5));
    int ox = (width - ow) / 2, oy = (height - oh) / 2;
    for (int y = 0; y < oh; y++) {
        for (int x = 0; x < ow; x++) {
            double fx0 = x / scale, fx1 = (x + 1) / scale, fy0 = y / scale, fy1 = (y + 1) / scale;
            double acc[4] = {0, 0, 0, 0}, total = 0;
            for (int sy = (int)fy0; sy < (int)ceil(fy1) && sy < h; sy++) {
                double wy = Lo(fy1, sy + 1.0) - Hi(fy0, (double)sy);
                if (fy1 - fy0 < 1) {
                    wy = 1;
                }
                for (int sx = (int)fx0; sx < (int)ceil(fx1) && sx < w; sx++) {
                    double wx = Lo(fx1, sx + 1.0) - Hi(fx0, (double)sx);
                    if (fx1 - fx0 < 1) {
                        wx = 1;
                    }
                    unsigned char* p = img.At(sx + x0, sy + y0);
                    double weight = wx * wy, a = p[3] / 255.0;
                    acc[0] += p[0] * a * weight;
                    acc[1] += p[1] * a * weight;
                    acc[2] += p[2] * a * weight;
                    acc[3] += a * weight;
                    total += weight;
                }
            }
            if (total <= 0 || acc[3] <= 0) {
                continue;
            }
            unsigned char* d = &rgba[((size_t)(y + oy) * width + x + ox) * 4];
            for (int c = 0; c < 3; c++) {
                d[c] = (unsigned char)Lo(255.0, acc[c] / acc[3] + 0.5);
            }
            d[3] = (unsigned char)Lo(255.0, acc[3] / total * 255 + 0.5);
        }
    }
}

} // namespace

bool TF_Encyclopedia_Render(const char* ini, int faction, unsigned char* rgba, int width, int height)
{
    TFEncSprite sprite;
    if (!TF_Encyclopedia_Sprite(ini, faction, &sprite)) {
        return false;
    }
    if (!TilesRead) {
        Read_Tilesets();
    }
    std::map<std::string, Tile>::const_iterator tile = Tiles.find(Upper(sprite.Art));
    if (tile == Tiles.end() || tile->second.Frame.empty()) {
        return false;
    }
    const Tile& art = tile->second;
    Image body;
    bool ok = false;
    std::map<std::string, Tile>::const_iterator built = Tiles.find(Upper(sprite.Art) + "MAKE");
    if (sprite.Body >= 0) {
        ok = Read_Frame(art, sprite.Body, body);
    } else if (sprite.Group == TF_ENC_STRUCTURES && built != Tiles.end() && !built->second.Frame.empty()) {
        ok = Read_Frame(built->second, built->second.Frame.rbegin()->first, body);
        if (ok) {
            Drop_Specks(body);
        }
    } else {
        int count = (int)art.Frame.size();
        int facings = count >= 32 ? 32 : Hi(count, 1);
        int shape = sprite.Group == TF_ENC_INFANTRY ? INFANTRY_FACING : (FACING * facings + 16) / 32 % facings;
        ok = Read_Frame(art, shape, body);
    }
    if (!ok) {
        ok = Read_Frame(art, art.Frame.begin()->first, body);
    }
    if (!ok) {
        return false;
    }
    if (sprite.Layers > 0) {
        int side = Hi(body.Width, body.Height) * 2;
        Image canvas(side, side);
        Composite(canvas, body, (side - body.Width) / 2, (side - body.Height) / 2);
        for (int l = 0; l < sprite.Layers; l++) {
            std::map<std::string, Tile>::const_iterator over = Tiles.find(Upper(sprite.Layer[l].Art));
            Image layer;
            if (over != Tiles.end() && Read_Frame(over->second, sprite.Layer[l].Frame, layer)) {
                int x = side / 2 + (int)floor(sprite.Layer[l].X * HD_PER_CLASSIC + 0.5) - layer.Width / 2;
                int y = side / 2 + (int)floor(sprite.Layer[l].Y * HD_PER_CLASSIC + 0.5) - layer.Height / 2;
                Composite(canvas, layer, x, y);
            }
        }
        body = canvas;
    }
    House_Colour(body, TEAMS[sprite.Team]);
    Fit(body, rgba, width, height);
    return true;
}
