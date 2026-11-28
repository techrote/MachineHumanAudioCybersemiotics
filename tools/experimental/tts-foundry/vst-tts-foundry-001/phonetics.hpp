#pragma once
#include <array>
#include <cctype>
#include <cstdint>
#include <string_view>

namespace mhac::tts {

enum class Phone : std::uint8_t {
    Pause, A, E, I, O, U, Schwa,
    B, D, G, K, P, T, M, N, R, L, F, V, S, Z, Sh, Ch, Th, H, W, Y, J, Ng
};

struct PhoneSpec {
    float f1, f2, f3;
    float voiced;
    float noise;
    float duration;
    float gain;
};

constexpr PhoneSpec spec(Phone p) noexcept {
    switch (p) {
        case Phone::A:     return {750.f, 1200.f, 2600.f, 1.f, .02f, .13f, .90f};
        case Phone::E:     return {520.f, 1900.f, 2700.f, 1.f, .02f, .12f, .86f};
        case Phone::I:     return {300.f, 2300.f, 3000.f, 1.f, .01f, .11f, .84f};
        case Phone::O:     return {500.f,  900.f, 2500.f, 1.f, .02f, .13f, .88f};
        case Phone::U:     return {350.f,  800.f, 2200.f, 1.f, .02f, .13f, .86f};
        case Phone::Schwa: return {550.f, 1500.f, 2500.f, 1.f, .02f, .10f, .80f};
        case Phone::B:     return {450.f, 1100.f, 2500.f, .6f, .15f, .065f, .75f};
        case Phone::D:     return {500.f, 1600.f, 2700.f, .55f,.18f, .060f, .74f};
        case Phone::G:     return {400.f, 1300.f, 2400.f, .55f,.16f, .070f, .76f};
        case Phone::K:     return {350.f, 1800.f, 3000.f, 0.f, .90f, .055f, .68f};
        case Phone::P:     return {400.f, 1000.f, 2400.f, 0.f, .90f, .050f, .66f};
        case Phone::T:     return {450.f, 1900.f, 3200.f, 0.f, .95f, .050f, .66f};
        case Phone::M:     return {300.f, 1000.f, 2200.f, 1.f, .03f, .085f, .76f};
        case Phone::N:     return {350.f, 1500.f, 2500.f, 1.f, .04f, .080f, .76f};
        case Phone::Ng:    return {300.f, 1200.f, 2300.f, 1.f, .04f, .090f, .74f};
        case Phone::R:     return {400.f, 1300.f, 1700.f, 1.f, .03f, .085f, .80f};
        case Phone::L:     return {450.f, 1400.f, 2600.f, 1.f, .03f, .080f, .80f};
        case Phone::F:     return {300.f, 1500.f, 3300.f, 0.f, .85f, .080f, .62f};
        case Phone::V:     return {350.f, 1400.f, 3100.f, .6f, .50f, .080f, .70f};
        case Phone::S:     return {250.f, 2200.f, 4200.f, 0.f, 1.00f, .085f, .62f};
        case Phone::Z:     return {300.f, 2100.f, 3900.f, .6f, .65f, .085f, .70f};
        case Phone::Sh:    return {300.f, 1800.f, 3300.f, 0.f, .95f, .090f, .64f};
        case Phone::Ch:    return {350.f, 1900.f, 3500.f, .1f, .95f, .075f, .66f};
        case Phone::Th:    return {350.f, 1600.f, 3000.f, .1f, .80f, .080f, .64f};
        case Phone::H:     return {500.f, 1500.f, 2600.f, 0.f, .65f, .070f, .58f};
        case Phone::W:     return {350.f,  900.f, 2200.f, 1.f, .02f, .075f, .78f};
        case Phone::Y:     return {300.f, 2200.f, 3000.f, 1.f, .02f, .070f, .78f};
        case Phone::J:     return {350.f, 1800.f, 3100.f, .5f, .55f, .075f, .70f};
        case Phone::Pause: default: return {500.f, 1500.f, 2500.f, 0.f, 0.f, .080f, 0.f};
    }
}

struct PhrasePlan {
    std::array<Phone, 96> phones{};
    std::uint16_t count = 0;
    bool truncated = false;

    bool push(Phone p) noexcept {
        if (count >= phones.size()) { truncated = true; return false; }
        phones[count++] = p;
        return true;
    }
    bool valid() const noexcept { return count > 0; }
};

inline char lower_ascii(char c) noexcept {
    return (c >= 'A' && c <= 'Z') ? static_cast<char>(c + ('a' - 'A')) : c;
}

inline bool vowel(char c) noexcept { return c=='a'||c=='e'||c=='i'||c=='o'||c=='u'||c=='y'; }

// Bounded, allocation-free English-like grapheme-to-phone sketch. This is deliberately
// a musical pronunciation planner, not a linguistic claim or production-quality G2P.
inline PhrasePlan compile_text(std::string_view text) noexcept {
    PhrasePlan out{};
    for (std::size_t i=0; i<text.size() && out.count<out.phones.size(); ++i) {
        const char c = lower_ascii(text[i]);
        const char n = (i+1<text.size()) ? lower_ascii(text[i+1]) : '\0';
        if (c==' ' || c=='\t' || c=='\n' || c=='-' || c=='/' || c=='.' || c==',' || c==';' || c==':') {
            if (out.count && out.phones[out.count-1] != Phone::Pause) out.push(Phone::Pause);
            continue;
        }
        if (c<'a' || c>'z') continue;
        if (c=='t' && n=='h') { out.push(Phone::Th); ++i; continue; }
        if (c=='s' && n=='h') { out.push(Phone::Sh); ++i; continue; }
        if (c=='c' && n=='h') { out.push(Phone::Ch); ++i; continue; }
        if (c=='n' && n=='g') { out.push(Phone::Ng); ++i; continue; }
        if (c=='p' && n=='h') { out.push(Phone::F); ++i; continue; }
        if (c=='q' && n=='u') { out.push(Phone::K); out.push(Phone::W); ++i; continue; }
        switch (c) {
            case 'a': out.push(Phone::A); break;
            case 'e': out.push(Phone::E); break;
            case 'i': out.push(Phone::I); break;
            case 'o': out.push(Phone::O); break;
            case 'u': out.push(Phone::U); break;
            case 'b': out.push(Phone::B); break;
            case 'c': out.push(n=='e'||n=='i'||n=='y' ? Phone::S : Phone::K); break;
            case 'd': out.push(Phone::D); break;
            case 'f': out.push(Phone::F); break;
            case 'g': out.push(n=='e'||n=='i'||n=='y' ? Phone::J : Phone::G); break;
            case 'h': out.push(Phone::H); break;
            case 'j': out.push(Phone::J); break;
            case 'k': out.push(Phone::K); break;
            case 'l': out.push(Phone::L); break;
            case 'm': out.push(Phone::M); break;
            case 'n': out.push(Phone::N); break;
            case 'p': out.push(Phone::P); break;
            case 'r': out.push(Phone::R); break;
            case 's': out.push(Phone::S); break;
            case 't': out.push(Phone::T); break;
            case 'v': out.push(Phone::V); break;
            case 'w': out.push(Phone::W); break;
            case 'x': out.push(Phone::K); out.push(Phone::S); break;
            case 'y': out.push(Phone::Y); break;
            case 'z': out.push(Phone::Z); break;
            default: break;
        }
    }
    if (!out.count) out.push(Phone::Pause);
    return out;
}

inline PhrasePlan phrase_program(unsigned index) noexcept {
    static constexpr std::array<std::string_view,8> phrases{{
        "machine voice", "hello world", "the word grows a mouth", "signal becomes song",
        "artificial articulation", "uncertain source", "sound poetry", "we speak in circuits"
    }};
    return compile_text(phrases[index % phrases.size()]);
}

} // namespace mhac::tts
