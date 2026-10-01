/*
 * bk2dump: decode Bink 2 (.bk2) video frames with RAD's own bink2w32.dll and
 * stream them as raw 32-bit BGRX to stdout.
 *
 *   bk2dump.exe info     <file.bk2>
 *   bk2dump.exe dump     <file.bk2> <first> <last> <step> [surface]
 *   bk2dump.exe dumplist <file.bk2> <listfile> [surface]
 *
 * Frame numbers are 0-based (frame 0 is the first frame), matching ffmpeg's
 * `n`. `last` of -1 means the final frame. `listfile` holds whitespace
 * separated frame numbers in ascending order.
 *
 * Every frame written is a 16-byte header {'BKFR', frame, width, height}
 * followed by width*height*4 bytes (B,G,R,X). Bink is inter-coded, so every
 * frame up to the last requested one is decoded; only requested frames are
 * colour-converted and written. Audio tracks are never opened. The DLL is
 * loaded from the executable's directory. Surface 3 (BINKSURFACE32) gives
 * BGRX byte order.
 */
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <io.h>
#include <fcntl.h>

typedef unsigned int U32;
typedef int S32;
typedef void *HBINK;

typedef HBINK (__stdcall *pBinkOpen)(const char *, U32);
typedef S32 (__stdcall *pBinkDoFrame)(HBINK);
typedef void (__stdcall *pBinkNextFrame)(HBINK);
typedef S32 (__stdcall *pBinkCopyToBuffer)(HBINK, void *, S32, U32, U32, U32, U32);
typedef void (__stdcall *pBinkClose)(HBINK);
typedef char *(__stdcall *pBinkGetError)(void);
typedef void (__stdcall *pBinkSetSoundTrack)(U32, U32 *);

#define BINKSNDTRACK 0x00004000u
#define BINKNOSKIP   0x00080000u
#define BINKCOPYALL  0x80000000u

static int cmp_u32(const void *a, const void *b)
{
    U32 x = *(const U32 *)a, y = *(const U32 *)b;
    return x < y ? -1 : x > y;
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "usage: bk2dump info|dump|dumplist file.bk2 ...\n");
        return 2;
    }
    HMODULE dll = LoadLibraryA("bink2w32.dll");
    if (!dll) { fprintf(stderr, "cannot load bink2w32.dll (%lu)\n", GetLastError()); return 1; }
#define GET(t, v, n) t v = (t)GetProcAddress(dll, n); if (!v) { fprintf(stderr, "missing %s\n", n); return 1; }
    GET(pBinkOpen, BinkOpen, "_BinkOpen@8");
    GET(pBinkDoFrame, BinkDoFrame, "_BinkDoFrame@4");
    GET(pBinkNextFrame, BinkNextFrame, "_BinkNextFrame@4");
    GET(pBinkCopyToBuffer, BinkCopyToBuffer, "_BinkCopyToBuffer@28");
    GET(pBinkClose, BinkClose, "_BinkClose@4");
    GET(pBinkGetError, BinkGetError, "_BinkGetError@0");
    GET(pBinkSetSoundTrack, BinkSetSoundTrack, "_BinkSetSoundTrack@8");

    U32 tracks[1] = {0};
    BinkSetSoundTrack(0, tracks);
    HBINK b = BinkOpen(argv[2], BINKSNDTRACK | BINKNOSKIP);
    if (!b) { fprintf(stderr, "BinkOpen failed: %s\n", BinkGetError()); return 1; }
    U32 *h = (U32 *)b;
    U32 w = h[0], ht = h[1], frames = h[2], rate = h[5], div = h[6];

    if (!strcmp(argv[1], "info")) {
        printf("width=%u height=%u frames=%u fps_num=%u fps_den=%u\n", w, ht, frames, rate, div);
        BinkClose(b);
        return 0;
    }

    U32 *want = NULL, nwant = 0, surface = 3;
    if (!strcmp(argv[1], "dump")) {
        if (argc < 6) { fprintf(stderr, "dump needs first last step\n"); return 2; }
        long first = atol(argv[3]), last = atol(argv[4]), step = atol(argv[5]);
        if (argc > 6) surface = (U32)strtoul(argv[6], 0, 0);
        if (first < 0) first = 0;
        if (last < 0 || last >= (long)frames) last = (long)frames - 1;
        if (step < 1) step = 1;
        want = (U32 *)malloc(sizeof(U32) * (frames + 1));
        for (long f = first; f <= last; f += step) want[nwant++] = (U32)f;
    } else if (!strcmp(argv[1], "dumplist")) {
        if (argc < 4) { fprintf(stderr, "dumplist needs a list file\n"); return 2; }
        if (argc > 4) surface = (U32)strtoul(argv[4], 0, 0);
        FILE *lf = fopen(argv[3], "r");
        if (!lf) { fprintf(stderr, "cannot open %s\n", argv[3]); return 1; }
        U32 cap = 1024; want = (U32 *)malloc(sizeof(U32) * cap);
        long v;
        while (fscanf(lf, "%ld", &v) == 1) {
            if (v < 0 || v >= (long)frames) continue;
            if (nwant == cap) { cap *= 2; want = (U32 *)realloc(want, sizeof(U32) * cap); }
            want[nwant++] = (U32)v;
        }
        fclose(lf);
        qsort(want, nwant, sizeof(U32), cmp_u32);
    } else {
        fprintf(stderr, "unknown mode %s\n", argv[1]);
        return 2;
    }
    if (nwant == 0) { BinkClose(b); return 0; }

    _setmode(_fileno(stdout), _O_BINARY);
    size_t pitch = (size_t)w * 4;
    unsigned char *buf = (unsigned char *)malloc(pitch * ht);
    if (!buf) { fprintf(stderr, "oom\n"); return 1; }

    U32 wi = 0, lastwant = want[nwant - 1];
    for (U32 f = 0; f <= lastwant && f < frames; f++) {
        BinkDoFrame(b);
        if (wi < nwant && want[wi] == f) {
            BinkCopyToBuffer(b, buf, (S32)pitch, ht, 0, 0, surface | BINKCOPYALL);
            U32 hdr[4] = {0x52464b42u, f, w, ht};
            fwrite(hdr, 4, 4, stdout);
            fwrite(buf, 1, pitch * ht, stdout);
            while (wi < nwant && want[wi] == f) wi++;
        }
        if (f + 1 < frames) BinkNextFrame(b);
    }
    fflush(stdout);
    free(buf);
    free(want);
    BinkClose(b);
    return 0;
}
