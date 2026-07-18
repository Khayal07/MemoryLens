// Azerbaijani strings. Must mirror en.ts key-for-key.
export const az: Record<string, string> = {
  // common
  "common.back": "Geri",
  "common.loading": "Yüklənir…",
  "common.done": "Hazırdır",
  "common.cancel": "Ləğv et",
  "common.save": "Yadda saxla",
  "common.viewSource": "Mənbəyə bax ↗",
  "common.startRecalling": "Xatırlamağa başla →",
  "common.genericError": "Nəsə səhv oldu.",

  // language toggle
  "lang.aria": "Dili dəyiş",
  "lang.en": "EN",
  "lang.az": "AZ",

  // nav / layout
  "nav.collections": "Kolleksiyalar",
  "nav.history": "Tarixçə",
  "nav.analytics": "Analitika",
  "nav.constellation": "Bürc",
  "nav.daily": "Gündəlik",
  "nav.signOut": "Çıxış",
  "nav.signIn": "Daxil ol",
  "nav.createAccount": "Hesab yarat",
  "nav.menu": "Menyu",
  "nav.skip": "Məzmuna keç",
  "nav.home": "MemoryLens ana səhifə",

  // category select
  "category.eyebrow": "Yarımçıq xatırlayırsan? Buradan başla",
  "category.title1": "Az qalıb.",
  "category.title2": "Fokusa gətir.",
  "category.subtitle":
    "Xatırladığın parçanı təsvir et — biz real kataloqda axtarıb ən ehtimallı uyğunluğu, nə qədər əmin olduğumuzu və səbəbini göstəririk.",
  "category.errorTitle": "Kateqoriyalar yüklənmədi.",
  "category.errorHint": "API işləyir? Bir azdan yeniləməyi sınayın.",
  "category.searchThis": "Bu kateqoriyada axtar",
  "category.name.movies": "Filmlər",
  "category.name.tv": "Seriallar",
  "category.name.songs": "Mahnılar",
  "category.name.books": "Kitablar",
  "category.name.games": "Oyunlar",
  "category.name.actors": "Aktyorlar",
  "category.desc.movies": "Bir səhnə, tək otaq, tanış gələn bir üz",
  "category.desc.tv": "O serial — hadisənin baş verdiyi",
  "category.desc.songs": "Bir misra, bir əhval, xorda yağış",
  "category.desc.books": "Əjdahalar, əlçatmaz bir ad",
  "category.desc.games": "Sarı saç, illərlə təkrar keçdiyin mərhələ",
  "category.desc.actors": "Həmişə pis obraz, amma adı yadda deyil",

  // auth
  "auth.login.title": "Yenidən xoş gəldin",
  "auth.login.subtitle": "Axtarış tarixçəni saxlamaq üçün daxil ol.",
  "auth.login.submit": "Daxil ol",
  "auth.login.busy": "Daxil olunur…",
  "auth.login.footerPre": "Yenisən?",
  "auth.login.footerLink": "Hesab yarat",
  "auth.login.failed": "Daxil olmaq alınmadı.",
  "auth.register.title": "Hesab yarat",
  "auth.register.subtitle": "Hər axtarışı saxla və qaldığın yerdən davam et.",
  "auth.register.submit": "Hesab yarat",
  "auth.register.busy": "Yaradılır…",
  "auth.register.short": "Şifrə ən azı 8 simvol olmalıdır.",
  "auth.register.footerPre": "Artıq hesabın var?",
  "auth.register.footerLink": "Daxil ol",
  "auth.register.failed": "Hesab yaradıla bilmədi.",
  "auth.field.email": "E-poçt",
  "auth.field.password": "Şifrə",

  // search
  "search.allCategories": "← Bütün kateqoriyalar",
  "search.placeholder": "Yarımçıq xatırladığın {category} təsvir et…",
  "search.ariaDescribe": "Xatırladığını təsvir et",
  "search.fragmentPlaceholder": "Xatırladığın ilk parçanı yaz…",
  "search.hintFragments": "Enter parça əlavə edir · Xatırla hamısını birlikdə axtarır",
  "search.hintText": "Axtarmaq üçün Enter · Yeni sətir üçün Shift+Enter",
  "search.focusing": "Fokuslanır…",
  "search.recall": "Xatırla",
  "search.toFreeText": "Sərbəst mətnə keç",
  "search.toFragment": "Parça rejiminə keç",
  "search.freeTextTitle": "Sərbəst mətn",
  "search.fragmentsTitle": "Parçalar",
  "search.bestMatch": "Ən yaxşı uyğunluq",
  "search.otherPossibilities": "Digər ehtimallar",
  "search.nothingMatched": "{category} üzrə uyğunluq tapılmadı.",
  "search.nothingHint": "Daha çox detal yaz — bir səhnə, personaj, hiss.",
  "search.ex.movies.1": "On iki nəfər bir otaqda hökm üstündə mübahisə edir",
  "search.ex.movies.2": "Bir kişi yuxunun içinə fikir yerləşdirir",
  "search.ex.tv.1": "Kimya müəllimi narkotik bişirməyə başlayır",
  "search.ex.tv.2": "Uşaqlar və başqa ölçüdən gələn bir canavar",
  "search.ex.songs.1": "Yağışda gəzməkdən oxuyan bir kişi",
  "search.ex.songs.2": "Bir adamı öldürmək haqqında operatik rok mahnısı",
  "search.ex.books.1": "Bir hobbit, bir əjdaha və oğurlanmış xəzinə",
  "search.ex.books.2": "Bir oğlan əjdaha yumurtası tapır və sehr öyrənir",
  "search.ex.games.1": "Sürətlə üzük yığan mavi kirpi",
  "search.ex.games.2": "Açıq dünyada qılıncla şahzadəni xilas edən qəhrəman",
  "search.ex.actors.1": "Həmişə mafiya və cinayət başçısı rolunda olur",
  "search.ex.actors.2": "Titanik və Inception filmlərindəki aktyor",

  // result card
  "result.aiKnowledge": "✦ Süni intellekt bilgisi",
  "result.why": "niyə?",
  "result.whyAria": "Bu əminlik niyə? Siqnal bölgüsünü aç/bağla",

  // clarify
  "clarify.oneMore": "Bir detal da",
  "clarify.answerPlaceholder": "Cavabın…",
  "clarify.answerAria": "Dəqiqləşdirici suala cavab ver",
  "clarify.refine": "Dəqiqləşdir ↺",

  // mismatch
  "mismatch.looksLike": "Bu daha çox {category} kimi görünür.",
  "mismatch.switchTo": "{category} keç",

  // save
  "save.aria": "Kolleksiyaya əlavə et",
  "save.saveTo": "Buraya saxla",
  "save.noCollections": "Hələ kolleksiya yoxdur.",
  "save.newCollection": "Yeni kolleksiya…",
  "save.add": "Əlavə et",

  // feedback
  "feedback.rateAria": "Bu uyğunluğu qiymətləndir",
  "feedback.good": "Yaxşı uyğunluq?",
  "feedback.goodAria": "Yaxşı uyğunluq",
  "feedback.badAria": "Pis uyğunluq",

  // share
  "share.copied": "Link kopyalandı!",
  "share.creating": "Yaradılır…",
  "share.share": "Paylaş",
  "share.prompt": "Bu paylaşım linkini kopyala:",

  // similar
  "similar.moreLikeThis": "Buna bənzər",

  // voice
  "voice.english": "İngiliscə",
  "voice.azerbaijani": "Azərbaycanca",
  "voice.langAria": "Nitq dili: {lang} — dəyişmək üçün klikləyin",
  "voice.stopAria": "Səs girişini dayandır",
  "voice.speakAria": "Xatirəni səslə de",

  // fragment board
  "fragment.addAnother": "Daha bir parça əlavə et…",
  "fragment.removeAria": "Parçanı sil: {f}",
  "fragment.addAria": "Xatirə parçası əlavə et",

  // confidence
  "confidence.inFocus": "fokusda",
  "confidence.coming": "fokusa gəlir",
  "confidence.fuzzy": "hələ dumanlı",
  "confidence.focusingLower": "fokuslanır…",
  "confidence.ariaValue": "Əminlik {pct} faiz",

  // breakdown
  "breakdown.sumMany":
    "{total}% — {n} müstəqil siqnalın cəmidir, heç biri təkbaşına üstün gələ bilməz:",
  "breakdown.sumOne": "Bu {total}% haradan gəlir:",
  "breakdown.llm.label": "Süni intellektin qərarı",
  "breakdown.llm.desc": "Süni intellekt bu elementi xatirənə nə qədər güclü uyğun sayır.",
  "breakdown.rerank.label": "Uyğunluq yoxlaması",
  "breakdown.rerank.desc": "Yoxlayıcı model sözlərini bu elementin təsviri ilə tutuşdurur.",
  "breakdown.retrieval.label": "Kataloqdan tapılma",
  "breakdown.retrieval.desc": "Kataloqun özündə axtaranda bu element nə qədər yuxarı çıxdı.",
  "breakdown.feedback.label": "İcma səsləri",
  "breakdown.feedback.desc": "İstifadəçilərin bəyənmə/bəyənməmələri balı zamanla dəyişir.",
  "breakdown.ai_knowledge.label": "Süni intellektin dünya bilgisi",
  "breakdown.ai_knowledge.desc":
    "Bu cavab kataloqumuzda yoxdur — süni intellekt onu öz real dünya bilgisindən adlandırıb. Kataloq məlumatı ilə yoxlaya bilmədiyimiz üçün əminlik 90%-lə məhdudlaşır.",

  // landing
  "landing.sentence": "on iki qəzəbli insan bir otaqda hökm üstündə mübahisə edir…",
  "landing.scrollHint": "fokuslamaq üçün sürüşdür ↓",
  "landing.youType": "Xatırladığını yazırsan",
  "landing.findsReal": "…və o, əsl olanı tapır",
  "landing.movieDesc":
    "İsti bir otaqda bağlı qalmış on iki münsif, biri təqsirsiz səs verir.",
  "landing.s3.title": "Yarımçıq xatirələrin altı rəfi.",
  "landing.s3.subtitle": "Real kataloqlar — uydurma cavab yoxdur. Bir rəf seç və parçanı təsvir et.",
  "landing.s4.title": "Dilinin ucunda qalan o şey?",
  "landing.s4.subtitle":
    "Hər tapıntını saxlamaq üçün hesab yarat — tarixçə, kolleksiyalar, xatirə bürcün və gündəlik təxmin oyunu.",
  "landing.s4.signIn": "Daxil ol ↗",

  // collections
  "collections.eyebrow": "Saxlanılan",
  "collections.title": "Kolleksiyaların",
  "collections.createPlaceholder": "Yeni kolleksiya yarat…",
  "collections.create": "Yarat",
  "collections.loadError": "Kolleksiyaların yüklənmədi.",
  "collections.emptyTitle": "Hələ kolleksiya yoxdur.",
  "collections.emptyHint": "Axtar, sonra nəticədə ✦ toxunub buraya saxla.",
  "collections.rename": "Adını dəyiş",
  "collections.delete": "Sil",
  "collections.empty": "Boş — nəticələri ✦ ilə buraya saxla.",
  "collections.removeAria": "{title} sil",

  // history
  "history.eyebrow": "Axtarışların",
  "history.title": "Nə axtarmısan",
  "history.viewAria": "Tarixçə görünüşü",
  "history.lane": "◧ Xatirə Yolu",
  "history.list": "☰ Siyahı",
  "history.loadError": "Tarixçən yüklənmədi.",
  "history.emptyTitle": "Hələ axtarış yoxdur.",
  "history.results": "{count} nəticə",
  "history.timelineAria": "Axtarış zaman xətti",
  "history.bestAria": "{query} — ən yaxşı uyğunluq {title}",
  "history.unknown": "naməlum",

  // analytics
  "analytics.eyebrow": "İstifadə",
  "analytics.title": "Analitika",
  "analytics.loadError": "Analitika yüklənmədi.",
  "analytics.total": "Ümumi axtarış",
  "analytics.last7": "Son 7 gün",
  "analytics.avgConfidence": "Orta əminlik",
  "analytics.grounded": "Kataloqdan",
  "analytics.byCategory": "Kateqoriyalara görə axtarış",
  "analytics.feedback": "Rəy",
  "analytics.upvotes": "👍 Bəyənmə",
  "analytics.downvotes": "👎 Bəyənməmə",
  "analytics.topQueries": "Ən çox axtarılan",
  "analytics.noSearches": "Hələ axtarış yoxdur.",
  "analytics.noData": "Hələ məlumat yoxdur.",

  // constellation
  "constellation.eyebrow": "Səmanız",
  "constellation.title": "Xatirə Bürcü",
  "constellation.subtitle":
    "Hər tapıntı bir ulduza çevrilir — rəng kateqoriyanı, ölçü nə qədər tez-tez göründüyünü bildirir, xətlər bənzər xatirələri birləşdirir. Tənha ulduzlar kataloqdan kənar, süni intellektin adlandırdığı tapıntılardır.",
  "constellation.loadError": "Bürcünüz çəkilə bilmədi.",
  "constellation.emptyTitle": "Hələ ulduz yoxdur.",
  "constellation.emptyHint": "Bir neçə xatirə axtar, burada görünəcəklər.",
  "constellation.mapAria": "Tapıntılarının ulduz xəritəsi",
  "constellation.zoomIn": "Böyüt",
  "constellation.zoomOut": "Kiçilt",
  "constellation.reset": "Görünüşü sıfırla",
  "constellation.seen": "görülüb ×{n}",

  // challenge
  "challenge.daily": "Gündəlik çağırış #{n}",
  "challenge.category": "Kateqoriya:",
  "challenge.title": "İpuclarından bugünkü sirri tap.",
  "challenge.locked": "Səhv təxmin növbəti ipucunu açır.",
  "challenge.lockedAria": "Kilidli ipucu",
  "challenge.guessPlaceholder": "Təxminin — bir {category} adı…",
  "challenge.guessAria": "Təxminin",
  "challenge.checking": "Yoxlanılır…",
  "challenge.guessN": "Təxmin {n}/{limit}",
  "challenge.notIt": "Deyil — yeni ipucu açıldı.",
  "challenge.solvedIn": "{n}/{limit}-də tapıldı",
  "challenge.outOfGuesses": "Təxminlər bitdi",
  "challenge.solvedMsg": "İti yaddaş — diyafraqma düz fokusa düşdü.",
  "challenge.failedMsg": "Bu gün əldən çıxdı. Sabah təzə sirr gətirir.",
  "challenge.copied": "Kopyalandı ✓",
  "challenge.shareResult": "Nəticəni paylaş",
  "challenge.unavailable": "Çağırış əlçatan deyil.",

  // shared result
  "shared.unavailableTitle": "Bu paylaşılan xatirə əlçatan deyil.",
  "shared.unavailableHint": "Link səhv ola bilər və ya axtarış silinib.",
  "shared.tryLink": "MemoryLens-i sına →",
  "shared.eyebrow": "Paylaşılan xatirə",
  "shared.noMatches": "Bu xatirə üçün uyğunluq tapılmadı.",
  "shared.recallOwn": "Öz xatirəni xatırla →",
};
