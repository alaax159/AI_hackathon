/* ===== PalJustice AI — App Logic ===== */

// ── i18n ──
const I18N = {
  ar: {
    appTitle: 'PalJustice AI 🇵🇸',
    langBtn: 'EN',
    homeTitle: 'PalJustice AI',
    homeSubtitle: 'مساعدك القانوني الذكي — القانون الأساسي الفلسطيني ٢٠٠٣',
    heroBadge: '🤖 مدعوم بالذكاء الاصطناعي',
    statArticles: 'مادة قانونية',
    statClinics: 'مركز مساعدة',
    statIntents: 'تصنيف قانوني',
    examplesLabel: 'أمثلة شائعة',
    micLabel: 'احكي مشكلتك',
    micStop: 'اضغط للإيقاف',
    orText: 'أو اكتب سؤالك',
    inputPlaceholder: 'اكتب مشكلتك القانونية...',
    send: '→',
    transcribing: 'جارٍ التحويل...',
    thinking: 'جارٍ التفكير...',
    viewSource: '📜 عرض النص القانوني',
    genForm: '📝 إنشاء نموذج',
    findHelp: '📍 مساعدة قانونية قريبة',
    disclaimer: 'هذه معلومات قانونية عامة فقط. يُرجى استشارة محامٍ مختص.',
    navHome: 'الرئيسية',
    navChat: 'المحادثات',
    navDemo: 'اختبار',
    navHelp: 'المساعدة',
    callTitle: 'اتصل بمساعدة قانونية',
    callSub: 'تواصل مع أقرب مركز مساعدة قانونية',
    nearbyTitle: 'مراكز مساعدة قريبة',
    directions: 'اتجاهات',
    callBtn: 'اتصال',
    noChats: 'لا توجد محادثات بعد',
    noChatsSub: 'اضغط على زر الميكروفون للبدء',
    noDocs: 'لا توجد مستندات بعد',
    noDocsSub: 'سيتم حفظ النماذج القانونية هنا',
    demoTitle: 'سيناريوهات اختبارية',
    demoSubtitle: 'بيانات حقيقية من القانون الأساسي الفلسطيني',
    sourcesLabel: 'المصادر القانونية',
    runTest: '💬 جرب هذا السؤال في المحادثة',
    examples: [
      'أخبرني صاحب البيت شفهياً أن عليّ المغادرة خلال 3 أيام',
      'اعتقلت الشرطة أخي بدون مذكرة',
      'فصلني صاحب العمل دون إشعار',
    ],
    urgency: { critical: 'حرج — تصرف فوراً', urgent: 'عاجل', standard: 'استشارة عامة' },
  },
  en: {
    appTitle: 'PalJustice AI 🇵🇸',
    langBtn: 'عربي',
    homeTitle: 'PalJustice AI',
    homeSubtitle: 'Your AI Legal Assistant — Palestinian Basic Law 2003',
    heroBadge: '🤖 AI-Powered',
    statArticles: 'Legal Articles',
    statClinics: 'Aid Centers',
    statIntents: 'Legal Categories',
    examplesLabel: 'Common examples',
    micLabel: 'Speak your problem',
    micStop: 'Tap to stop',
    orText: 'or type your question',
    inputPlaceholder: 'Describe your legal problem...',
    send: '→',
    transcribing: 'Transcribing...',
    thinking: 'Thinking...',
    viewSource: '📜 View Legal Source',
    genForm: '📝 Generate Form',
    findHelp: '📍 Find Legal Help',
    disclaimer: 'This is general legal information. Consult a licensed lawyer.',
    navHome: 'Home',
    navChat: 'Chat',
    navDemo: 'Demo',
    navHelp: 'Help',
    callTitle: 'Call Legal Aid',
    callSub: 'Connect with the nearest legal aid center',
    nearbyTitle: 'Nearby Legal Aid',
    directions: 'Directions',
    callBtn: 'Call',
    noChats: 'No conversations yet',
    noChatsSub: 'Tap the microphone to start',
    noDocs: 'No documents yet',
    noDocsSub: 'Generated legal forms will appear here',
    demoTitle: 'Test Scenarios',
    demoSubtitle: 'Real data from the Palestinian Basic Law',
    sourcesLabel: 'Legal Sources',
    runTest: '💬 Try this question in Chat',
    examples: [
      'My landlord told me I have 3 days to leave',
      'Police arrested my brother without a warrant',
      'My employer fired me without notice',
    ],
    urgency: { critical: 'Critical — act now', urgent: 'Urgent', standard: 'General inquiry' },
  }
};

// ── Test Scenarios Data ──
const TEST_SCENARIOS = {
  ar: [
    {
      id: 'eviction',
      icon: '🏠',
      category: 'إخلاء / السكن',
      question: 'أخبرني صاحب البيت شفهياً أن عليّ المغادرة خلال 3 أيام',
      triage: {
        level: 'urgent', color: 'amber',
        label: 'عاجل — تصرف خلال 7 أيام',
        deadline_hint: 'خلال 7 أيام: اجمع الأدلة وتواصل مع محامٍ'
      },
      answer: 'بموجب المادة (17) من القانون الأساسي الفلسطيني، يُعدّ الإخلاء الشفهي دون مذكرة قضائية باطلاً ولا أثر له قانوناً. للمستأجر الحق الكامل في البقاء حتى صدور حكم قضائي نهائي، وأي إجراء خارج نطاق القضاء يُعدّ انتهاكاً صريحاً لحقوق السكن المكفولة دستورياً بموجب المادتين 21 و23.',
      sources: [
        { article: 'المادة 17', title: 'الحق في السكن', text: 'لا يجوز تفتيش المساكن إلا بموجب أمر قضائي وفقاً للأحكام القانونية، ولكل شخص الحق في السكن الملائم.' },
        { article: 'المادة 21', title: 'الملكية الخاصة', text: 'الملكية الخاصة مصونة، ولا يجوز نزع ملكية أي شخص إلا للمصلحة العامة وبتعويض عادل وفق القانون.' },
        { article: 'المادة 23', title: 'حق التقاضي', text: 'لكل مواطن حق اللجوء إلى القضاء وذلك بطريقة يكفلها القانون.' },
      ],
      actionPlan: [
        { timeframe: 'الآن', action: 'لا تغادر المسكن — الأمر الشفهي لا قيمة قانونية له' },
        { timeframe: 'اليوم', action: 'التقط صوراً لأي إشعارات مكتوبة ووثّق كل شيء' },
        { timeframe: 'هذا الأسبوع', action: 'أرسل رداً كتابياً مستنداً للمواد 17 و21 و23' },
        { timeframe: 'خلال 30 يوم', action: 'تقدّم بشكوى قضائية إذا وصل إشعار رسمي' },
      ],
      clinic: { name: 'عيادة جامعة بيرزيت القانونية', city: 'رام الله', phone: '+970-2-298-2960' }
    },
    {
      id: 'criminal',
      icon: '🚨',
      category: 'اعتقال / حرية شخصية',
      question: 'اعتقلت الشرطة أخي بدون مذكرة اعتقال',
      triage: {
        level: 'critical', color: 'red',
        label: 'حرج — تصرف فوراً',
        deadline_hint: 'خلال ساعات: اتصل بمحامٍ ومنظمة حقوق الإنسان فوراً'
      },
      answer: 'القانون الأساسي (المادة 11) يكفل الحرية الشخصية. قانون الإجراءات الجزائية رقم 3 لسنة 2001 يُقيّد الاعتقال بقيود صارمة: المادة 29 تشترط أمراً من الجهة المختصة، والمادة 30 تُجيز الاعتقال بلا مذكرة فقط في الجرم المشهود. المادة 34 تُوجب تقديمه لنيابة عامة خلال 24 ساعة، والمادة 102 تكفل حق المحامٍ خلال التحقيق، والمادة 97 تكفل حق الصمت.',
      sources: [
        { article: 'المادة 11 — القانون الأساسي', title: 'الحرية الشخصية', text: 'الحرية الشخصية حق مكفول لكل إنسان، ولا يجوز القبض على أحد أو تفتيشه أو احتجازه أو تقييد حريته إلا وفق أحكام القانون.' },
        { article: 'المادة 29 — ق. الإجراءات الجزائية', title: 'حظر الاعتقال بغير أمر', text: 'لا يجوز اعتقال أي شخص أو سجنه إلا بأمر من الجهة المختصة وفق القانون. ويُعامَل كل موقوف معاملة تصون كرامته الإنسانية.' },
        { article: 'المادة 34 — ق. الإجراءات الجزائية', title: 'قاعدة 24 ساعة', text: 'يسمع الضابط القضائي أقوال الموقوف فوراً، وإن تعذّر الفصل أرسله مع محضر التوقيف إلى النائب العام المختص خلال 24 ساعة من التوقيف.' },
        { article: 'المادة 97 — ق. الإجراءات الجزائية', title: 'حق الصمت', text: 'للمتهم الحق في الصمت وعدم الإجابة على الأسئلة الموجهة إليه. ولا يُفسَّر صمته على أي وجه كاعتراف بالتهمة.' },
        { article: 'المادة 102 — ق. الإجراءات الجزائية', title: 'حق التمثيل القانوني', text: 'للمتهم الاستعانة بمحامٍ خلال التحقيق. وللمحامٍ الاطلاع على المحاضر السابقة وتقديم مذكراته وملاحظاته.' },
        { article: 'المادة 120 — ق. الإجراءات الجزائية', title: 'الحد الأقصى للاحتجاز', text: 'لا يجوز احتجاز المتهم مدة تتجاوز 45 يوماً إجمالاً خلال مرحلة التحقيق، ولا يجوز في أي حال أن تتجاوز مدة العقوبة المقررة للجريمة المنسوبة إليه.' },
      ],
      actionPlan: [
        { timeframe: 'الآن', action: 'التزم الصمت التام — المادة 97 من ق. الإجراءات تكفل حق الصمت ولا يُعدّ دليلاً عليك' },
        { timeframe: 'الآن', action: 'اطلب محامياً فوراً — المادة 102 تكفل ذلك وإذا تعذّر تعيّن المحكمة أحداً (المادة 244)' },
        { timeframe: 'خلال 24 ساعة', action: 'يجب تقديمه أمام النيابة خلال 24 ساعة (المادة 34). اطلب ذلك إذا لم يحدث' },
        { timeframe: 'خلال 24 ساعة', action: 'أصرّ على إبلاغه بالتهم — المادة 96 تُوجب على النيابة إخطاره قبل أي استجواب' },
        { timeframe: 'خلال 48 ساعة', action: 'الاحتجاز يستوجب أمراً قضائياً — الحد 15 يوماً (مادة 119) وإجمالاً 45 يوماً (مادة 120)' },
        { timeframe: 'هذا الأسبوع', action: 'أي اعتراف بالإكراه باطل (مادة 214 و273). وثّق أي سوء معاملة فوراً' },
      ],
      clinic: { name: 'الحق — مركز حقوق الإنسان', city: 'رام الله', phone: '+970-2-295-4646' }
    },
    {
      id: 'labor',
      icon: '💼',
      category: 'عمل / فصل تعسفي',
      question: 'فصلني صاحب العمل دون إشعار مسبق أو سبب واضح',
      triage: {
        level: 'standard', color: 'green',
        label: 'استشارة عامة — خلال 30 يوم',
        deadline_hint: 'خلال 30 يوم: راجع المستندات واطلب مشورة قانونية'
      },
      answer: 'تكفل المادة (25) من القانون الأساسي حقوق العمال وتحظر الفصل التعسفي غير المبرر. يحق للموظف الحصول على مكافأة نهاية خدمة وفترة إشعار أو تعويض مالي عنها وفقاً لقانون العمل الفلسطيني. رفع شكوى لدى وزارة العمل هو الخطوة الأولى للمطالبة بحقوقك.',
      sources: [
        { article: 'المادة 25', title: 'حقوق العمال', text: 'يحدد القانون الحد الأدنى للأجور، ويضمن نظام تأمين اجتماعي شامل لحماية حقوق العمال والموظفين.' },
        { article: 'المادة 26', title: 'حرية العمل', text: 'العمل حق ومسؤولية وشرف، وتسعى السلطة الوطنية إلى توفير فرص العمل لكل قادر عليه.' },
      ],
      actionPlan: [
        { timeframe: 'اليوم', action: 'احتفظ بكل المستندات — العقد، كشوف الراتب، الرسائل' },
        { timeframe: 'هذا الأسبوع', action: 'اطلب من صاحب العمل تقديم قرار الفصل كتابياً مع الأسباب' },
        { timeframe: 'هذا الأسبوع', action: 'تقدّم بشكوى رسمية لوزارة العمل الفلسطينية' },
        { timeframe: 'خلال 30 يوم', action: 'استشر محامياً عمالياً لتقييم التعويض المستحق' },
      ],
      clinic: { name: 'عيادة جامعة بيرزيت القانونية', city: 'رام الله', phone: '+970-2-298-2960' }
    },
  ],
  en: [
    {
      id: 'eviction',
      icon: '🏠',
      category: 'Housing / Eviction',
      question: 'My landlord verbally told me I have 3 days to leave',
      triage: {
        level: 'urgent', color: 'amber',
        label: 'Urgent — act within 7 days',
        deadline_hint: 'Within 7 days: gather evidence and contact a lawyer'
      },
      answer: 'Under Article 17 of the Palestinian Basic Law, a verbal eviction order without a court warrant is legally void and has no effect. The tenant has the full right to remain until a final court ruling is issued. Any action outside of the judicial process is a direct violation of constitutionally protected housing rights under Articles 21 and 23.',
      sources: [
        { article: 'Article 17', title: 'Right to Housing', text: 'Homes may not be searched or entered except by judicial order according to legal provisions. Everyone has the right to adequate housing.' },
        { article: 'Article 21', title: 'Private Property', text: 'Private property is protected. No person may be dispossessed except for the public good and with fair compensation according to law.' },
        { article: 'Article 23', title: 'Right to Appeal', text: 'Every citizen has the right to resort to the judiciary in the manner guaranteed by law.' },
      ],
      actionPlan: [
        { timeframe: 'Now', action: 'Do NOT leave — a verbal order has no legal standing' },
        { timeframe: 'Today', action: 'Photograph any written notices and document everything' },
        { timeframe: 'This week', action: 'Send a written reply citing Articles 17, 21, and 23' },
        { timeframe: 'Within 30 days', action: 'File a court complaint if a formal notice arrives' },
      ],
      clinic: { name: 'Birzeit University Legal Clinic', city: 'Ramallah', phone: '+970-2-298-2960' }
    },
    {
      id: 'criminal',
      icon: '🚨',
      category: 'Arrest / Personal Freedom',
      question: 'Police arrested my brother without a warrant',
      triage: {
        level: 'critical', color: 'red',
        label: 'Critical — act immediately',
        deadline_hint: 'Within hours: call a lawyer and human rights organization now'
      },
      answer: 'Basic Law Art. 11 guarantees personal freedom. Under Penal Procedure Law No. 3/2001: Art. 29 requires an order from competent authority for any arrest. Art. 30 allows warrantless arrest only for flagrant crimes. Art. 34 requires the accused to be brought before the Prosecutor within 24 hours. Art. 97 guarantees the right to silence, and Art. 102 guarantees legal counsel during investigation.',
      sources: [
        { article: 'Art. 11 — Basic Law', title: 'Personal Freedom', text: 'Personal freedom is a guaranteed right for all persons. No one may be arrested, searched, detained, or have their freedom restricted except in accordance with legal provisions.' },
        { article: 'Art. 29 — Penal Procedure Law No. 3/2001', title: 'No Arrest Without Authority', text: 'No person may be arrested or imprisoned except by order of the competent authority as set forth in the law. Every person arrested shall be treated in a manner that preserves his human dignity.' },
        { article: 'Art. 34 — Penal Procedure Law No. 3/2001', title: '24-Hour Rule', text: 'The judicial officer shall hear the statement of the arrested person immediately and send him to the competent Deputy-Prosecutor within twenty-four (24) hours of arrest.' },
        { article: 'Art. 97 — Penal Procedure Law No. 3/2001', title: 'Right to Silence', text: 'The accused shall have the right to remain silent and not to respond to any questions. His silence may not be construed as an admission of any charge.' },
        { article: 'Art. 102 — Penal Procedure Law No. 3/2001', title: 'Right to Counsel', text: 'The accused shall have the right to seek the assistance of counsel during the investigation. The counsel shall have the right to review investigation minutes and submit observations.' },
        { article: 'Art. 120 — Penal Procedure Law No. 3/2001', title: 'Maximum Detention Period', text: 'Total pre-trial detention during investigation shall not exceed forty-five (45) days in aggregate, and in no case may exceed the penalty prescribed for the offence charged.' },
      ],
      actionPlan: [
        { timeframe: 'Now', action: 'Stay completely silent — Art. 97 guarantees right to silence; silence cannot be used as evidence' },
        { timeframe: 'Now', action: 'Demand a lawyer immediately — Art. 102 (investigation) and Art. 244 (court-appointed for felonies)' },
        { timeframe: 'Within 24 hours', action: 'Must be brought before the Prosecutor within 24 hours (Art. 34). Demand this if it has not happened' },
        { timeframe: 'Within 24 hours', action: 'Insist on being told the charges — Art. 96 requires the Prosecutor to inform before any interrogation' },
        { timeframe: 'Within 48 hours', action: 'Detention needs a court order — max 15 days (Art. 119), total max 45 days (Art. 120)' },
        { timeframe: 'This week', action: 'Any confession under coercion is void (Art. 214 & 273). Document all mistreatment immediately' },
      ],
      clinic: { name: 'Al-Haq Human Rights Center', city: 'Ramallah', phone: '+970-2-295-4646' }
    },
    {
      id: 'labor',
      icon: '💼',
      category: 'Labor / Wrongful Termination',
      question: 'My employer fired me without notice or clear reason',
      triage: {
        level: 'standard', color: 'green',
        label: 'General inquiry — within 30 days',
        deadline_hint: 'Within 30 days: review documents and seek legal counsel'
      },
      answer: 'Article 25 of the Palestinian Basic Law protects workers\' rights and prohibits arbitrary dismissal. You are entitled to end-of-service pay, a notice period or compensation in lieu, according to Palestinian Labor Law. Filing a complaint with the Ministry of Labor is the first step to claiming your rights.',
      sources: [
        { article: 'Article 25', title: 'Workers\' Rights', text: 'The law specifies a minimum wage and guarantees a comprehensive social insurance system to protect the rights of workers and employees.' },
        { article: 'Article 26', title: 'Freedom to Work', text: 'Work is a right, responsibility, and honor. The National Authority strives to provide employment opportunities for all who are able.' },
      ],
      actionPlan: [
        { timeframe: 'Today', action: 'Keep all documents — contract, payslips, correspondence' },
        { timeframe: 'This week', action: 'Request a written termination letter with stated reasons' },
        { timeframe: 'This week', action: 'File a formal complaint with the Palestinian Ministry of Labor' },
        { timeframe: 'Within 30 days', action: 'Consult a labor lawyer to assess due compensation' },
      ],
      clinic: { name: 'Birzeit University Legal Clinic', city: 'Ramallah', phone: '+970-2-298-2960' }
    },
  ]
};

let currentLang = 'ar';
let currentTab = 'home';
let chatMessages = [];
let documents = [];

function t(key) { return I18N[currentLang][key] || I18N.en[key] || key; }

// ── Language Toggle ──
function toggleLang() {
  currentLang = currentLang === 'ar' ? 'en' : 'ar';
  document.body.classList.toggle('ltr', currentLang === 'en');
  document.documentElement.lang = currentLang;
  document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
  renderAll();
}

// ── Navigation ──
function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-' + tab).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
  if (tab === 'help') initMap();
}

// ── Render Everything ──
function renderAll() {
  document.getElementById('lang-btn').textContent = t('langBtn');

  // Home
  document.getElementById('home-title').textContent = t('homeTitle');
  document.getElementById('home-subtitle').textContent = t('homeSubtitle');
  document.getElementById('hero-badge').textContent = t('heroBadge');
  document.getElementById('stat-articles').textContent = t('statArticles');
  document.getElementById('stat-clinics').textContent = t('statClinics');
  document.getElementById('stat-intents').textContent = t('statIntents');
  document.getElementById('mic-label').textContent = t('micLabel');
  document.getElementById('or-text').textContent = t('orText');
  document.getElementById('text-input').placeholder = t('inputPlaceholder');
  document.getElementById('examples-label').textContent = t('examplesLabel');

  // Nav
  document.getElementById('nav-home-label').textContent = t('navHome');
  document.getElementById('nav-chat-label').textContent = t('navChat');
  document.getElementById('nav-demo-label').textContent = t('navDemo');
  document.getElementById('nav-help-label').textContent = t('navHelp');

  // Disclaimer
  document.querySelectorAll('.disclaimer').forEach(d => d.textContent = t('disclaimer'));

  renderExamples();
  renderChat();
  renderDemo();
  renderHelp();
}

function renderExamples() {
  const container = document.getElementById('examples');
  container.innerHTML = '';
  for (const ex of t('examples')) {
    const chip = document.createElement('button');
    chip.className = 'example-chip';
    chip.textContent = ex;
    chip.onclick = () => {
      document.getElementById('text-input').value = ex;
      submitQuestion(ex);
    };
    container.appendChild(chip);
  }
}

// ── Chat Rendering ──
function renderChat() {
  const container = document.getElementById('chat-messages');
  if (chatMessages.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <span class="icon">💬</span>
        <div>${t('noChats')}</div>
        <div style="margin-top:4px;font-size:12px">${t('noChatsSub')}</div>
      </div>`;
    return;
  }
  container.innerHTML = '';
  for (const msg of chatMessages) {
    if (msg.type === 'user') {
      const div = document.createElement('div');
      div.className = 'msg msg-user';
      div.textContent = msg.text;
      container.appendChild(div);
    } else if (msg.type === 'typing') {
      const div = document.createElement('div');
      div.className = 'typing-indicator';
      div.innerHTML = '<span></span><span></span><span></span>';
      div.id = 'typing-indicator';
      container.appendChild(div);
    } else if (msg.type === 'ai') {
      container.appendChild(buildAIMessage(msg));
    }
  }
  container.scrollTop = container.scrollHeight;
  const screen = document.getElementById('screen-chat');
  screen.scrollTop = screen.scrollHeight;
}

function buildAIMessage(msg) {
  const div = document.createElement('div');
  div.className = 'msg msg-ai';
  let html = '';

  if (msg.triage) {
    const color = msg.triage.color || 'green';
    const label = msg.triage.label || '';
    html += `<div class="msg-badge ${color}">● ${esc(label)}</div>`;
    if (msg.triage.deadline_hint) {
      html += `<div class="deadline-hint">${esc(msg.triage.deadline_hint)}</div>`;
    }
  }

  html += `<div class="msg-text">${esc(msg.text)}</div>`;

  if (msg.actionPlan && msg.actionPlan.length > 0) {
    html += '<div class="action-plan">';
    for (const step of msg.actionPlan) {
      html += `<div class="action-step">
        <span class="step-time">${esc(step.timeframe)}</span>
        <span class="step-text">${esc(step.action)}</span>
      </div>`;
    }
    html += '</div>';
  }

  if (msg.sources && msg.sources.length > 0) {
    for (const src of msg.sources) {
      html += `<div class="legal-card" onclick="this.classList.toggle('open')">
        <div class="legal-card-header">
          <span>${esc(src.article || '')} — ${esc(src.title || '')}</span>
          <span class="arrow">▼</span>
        </div>
        <div class="legal-card-body">
          <div class="legal-card-text">${esc(src.text || '')}</div>
        </div>
      </div>`;
    }
  }

  html += `<div class="msg-actions">
    <button class="msg-action-btn" onclick="showSources()">${t('viewSource')}</button>
    <button class="msg-action-btn" onclick="generateForm()">${t('genForm')}</button>
    <button class="msg-action-btn" onclick="switchTab('help')">${t('findHelp')}</button>
  </div>`;

  div.innerHTML = html;
  return div;
}

function esc(s) {
  const el = document.createElement('span');
  el.textContent = s || '';
  return el.innerHTML;
}

// ── Demo / Test Scenarios ──
function renderDemo() {
  const titleEl = document.getElementById('demo-title');
  const subtitleEl = document.getElementById('demo-subtitle');
  if (titleEl) titleEl.textContent = t('demoTitle');
  if (subtitleEl) subtitleEl.textContent = t('demoSubtitle');

  const container = document.getElementById('demo-scenarios');
  if (!container) return;
  container.innerHTML = '';

  const scenarios = TEST_SCENARIOS[currentLang] || TEST_SCENARIOS.ar;

  scenarios.forEach((s, i) => {
    const card = document.createElement('div');
    card.className = 'scenario-card';
    card.id = `scenario-${s.id}`;

    card.innerHTML = `
      <div class="scenario-header" onclick="toggleScenario('${s.id}')">
        <div class="scenario-left">
          <span class="scenario-icon">${s.icon}</span>
          <div class="scenario-info">
            <div class="scenario-category">${esc(s.category)}</div>
            <div class="scenario-question">"${esc(s.question)}"</div>
          </div>
        </div>
        <div class="scenario-right">
          <span class="scenario-badge ${s.triage.color}">${esc(s.triage.label)}</span>
          <span class="scenario-arrow">▼</span>
        </div>
      </div>
      <div class="scenario-body" id="scenario-body-${s.id}">
        ${buildScenarioBody(s)}
      </div>
    `;
    container.appendChild(card);

    // Auto-expand first scenario
    if (i === 0) setTimeout(() => toggleScenario(s.id), 150);
  });
}

function buildScenarioBody(s) {
  let html = '';

  html += `<div class="scenario-triage ${s.triage.color}">
    <strong>● ${esc(s.triage.label)}</strong>
    <div class="triage-hint">${esc(s.triage.deadline_hint)}</div>
  </div>`;

  html += `<p class="scenario-answer">${esc(s.answer)}</p>`;

  if (s.actionPlan && s.actionPlan.length > 0) {
    html += '<div class="action-plan">';
    for (const step of s.actionPlan) {
      html += `<div class="action-step">
        <span class="step-time">${esc(step.timeframe)}</span>
        <span class="step-text">${esc(step.action)}</span>
      </div>`;
    }
    html += '</div>';
  }

  if (s.sources && s.sources.length > 0) {
    html += `<div class="sources-label">${esc(t('sourcesLabel'))}</div>`;
    for (const src of s.sources) {
      html += `<div class="legal-card" onclick="this.classList.toggle('open')">
        <div class="legal-card-header">
          <span>${esc(src.article)} — ${esc(src.title)}</span>
          <span class="arrow">▼</span>
        </div>
        <div class="legal-card-body">
          <div class="legal-card-text">${esc(src.text)}</div>
        </div>
      </div>`;
    }
  }

  if (s.clinic) {
    html += `<div class="scenario-clinic">
      <span class="clinic-pin">📍</span>
      <div>
        <div class="clinic-name">${esc(s.clinic.name)}</div>
        <div class="clinic-meta">${esc(s.clinic.city)} · <a href="tel:${esc(s.clinic.phone)}" style="color:var(--green-800)">${esc(s.clinic.phone)}</a></div>
      </div>
    </div>`;
  }

  html += `<button class="run-test-btn" onclick="runScenario('${s.id}')">${t('runTest')}</button>`;

  return html;
}

function toggleScenario(id) {
  const body = document.getElementById(`scenario-body-${id}`);
  const card = document.getElementById(`scenario-${id}`);
  if (!body || !card) return;
  const isOpen = card.classList.contains('open');
  card.classList.toggle('open', !isOpen);
  body.style.maxHeight = isOpen ? '0' : body.scrollHeight + 'px';
}

function runScenario(id) {
  const scenarios = TEST_SCENARIOS[currentLang] || TEST_SCENARIOS.ar;
  const s = scenarios.find(x => x.id === id);
  if (!s) return;
  submitQuestion(s.question);
}

// ── Help Screen ──
let helpMap = null, helpMarkers = null;

function renderHelp() {
  document.getElementById('call-title').textContent = t('callTitle');
  document.getElementById('call-sub').textContent = t('callSub');
  document.getElementById('nearby-title').textContent = t('nearbyTitle');
  loadClinics();
}

function initMap() {
  if (helpMap) { helpMap.invalidateSize(); return; }
  if (typeof L === 'undefined') return;
  setTimeout(() => {
    helpMap = L.map('help-map', { scrollWheelZoom: false }).setView([31.95, 35.20], 8);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18, attribution: '© OpenStreetMap'
    }).addTo(helpMap);
    helpMarkers = L.layerGroup().addTo(helpMap);
    loadClinics();
  }, 200);
}

async function loadClinics() {
  try {
    const r = await fetch('/clinics?limit=5');
    if (!r.ok) return;
    const data = await r.json();
    renderClinics(data.clinics || []);
  } catch (e) { /* offline fallback ok */ }
}

function renderClinics(clinics) {
  const container = document.getElementById('clinics-list');
  container.innerHTML = '';
  const points = [];

  for (const c of clinics) {
    const card = document.createElement('div');
    card.className = 'clinic-card';
    const dist = c.distance_km != null ? ` · ${c.distance_km} km` : '';
    const tags = (c.specialties || []).map(s => `<span class="clinic-tag">${esc(s)}</span>`).join('');
    card.innerHTML = `
      <div class="clinic-name">${esc(c.name)}</div>
      <div class="clinic-meta">${esc(c.city)}, ${esc(c.region)}${dist}</div>
      <div class="clinic-tags">${tags}</div>
      <div class="clinic-actions">
        <button class="clinic-action-btn" onclick="window.open('tel:${esc(c.phone)}')">${t('callBtn')} ${esc(c.phone)}</button>
        <button class="clinic-action-btn" onclick="window.open('https://maps.google.com/?q=${c.latitude},${c.longitude}')">${t('directions')}</button>
      </div>`;
    container.appendChild(card);

    if (helpMap && helpMarkers && c.latitude && c.longitude) {
      L.marker([c.latitude, c.longitude])
        .bindPopup(`<b>${esc(c.name)}</b><br>${esc(c.city)}`)
        .addTo(helpMarkers);
      points.push([c.latitude, c.longitude]);
    }
  }
  if (helpMap && points.length) helpMap.fitBounds(points, { padding: [30, 30], maxZoom: 11 });
}

// ── Voice Recording ──
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recog = null, recognizing = false;
let mediaRecorder = null, chunks = [];

if (SR) {
  recog = new SR();
  recog.interimResults = true;
  recog.continuous = false;
  recog.maxAlternatives = 1;
}

function toggleRecording() {
  const wrapper = document.getElementById('mic-wrapper');
  const label = document.getElementById('mic-label');

  if (recognizing || (mediaRecorder && mediaRecorder.state === 'recording')) {
    stopRecording();
    return;
  }

  wrapper.classList.add('recording');
  label.textContent = t('micStop');

  if (recog) {
    recog.lang = currentLang === 'ar' ? 'ar-PS' : 'en-US';
    recog.onresult = (e) => {
      let txt = '';
      for (let i = 0; i < e.results.length; i++) txt += e.results[i][0].transcript;
      document.getElementById('transcription').textContent = txt;
      document.getElementById('transcription').classList.add('active');
      if (e.results[e.results.length - 1].isFinal) {
        stopRecording();
        submitQuestion(txt);
      }
    };
    recog.onerror = () => stopRecording();
    recog.onend = () => { if (recognizing) stopRecording(); };
    try {
      recog.start();
      recognizing = true;
      document.getElementById('transcription').textContent = '';
      document.getElementById('transcription').classList.add('active');
    } catch (e) { stopRecording(); }
  } else {
    startMediaRecording();
  }
}

async function startMediaRecording() {
  if (!navigator.mediaDevices) { stopRecording(); return; }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    chunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(chunks, { type: 'audio/webm' });
      document.getElementById('transcription').textContent = t('transcribing');
      const fd = new FormData();
      fd.append('audio', blob, 'speech.webm');
      if (currentLang !== 'auto') fd.append('language', currentLang);
      try {
        const r = await fetch('/transcribe', { method: 'POST', body: fd });
        if (!r.ok) throw new Error('Transcription failed');
        const data = await r.json();
        document.getElementById('transcription').textContent = data.text || '';
        if (data.text) submitQuestion(data.text);
      } catch (e) {
        document.getElementById('transcription').textContent = '';
      }
    };
    mediaRecorder.start();
  } catch (e) { stopRecording(); }
}

function stopRecording() {
  const wrapper = document.getElementById('mic-wrapper');
  const label = document.getElementById('mic-label');
  wrapper.classList.remove('recording');
  label.textContent = t('micLabel');
  document.getElementById('transcription').classList.remove('active');
  recognizing = false;
  if (recog) try { recog.stop(); } catch (e) {}
  if (mediaRecorder && mediaRecorder.state === 'recording') mediaRecorder.stop();
}

// ── Submit Question ──
async function submitQuestion(question) {
  if (!question || !question.trim()) return;
  const q = question.trim();

  chatMessages.push({ type: 'user', text: q });
  chatMessages.push({ type: 'typing' });
  switchTab('chat');
  renderChat();

  try {
    const resp = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q, language: currentLang, top_k: 3 }),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    chatMessages = chatMessages.filter(m => m.type !== 'typing');
    chatMessages.push({
      type: 'ai',
      text: data.answer,
      triage: data.triage,
      sources: data.sources || [],
      actionPlan: data.action_plan || [],
      intent: data.intent,
      clinics: data.clinics || [],
    });
    renderChat();
  } catch (err) {
    chatMessages = chatMessages.filter(m => m.type !== 'typing');
    chatMessages.push({ type: 'ai', text: 'Error: ' + err.message, sources: [], actionPlan: [] });
    renderChat();
  }
}

function handleTextSubmit() {
  const input = document.getElementById('text-input');
  const val = input.value.trim();
  if (val) {
    submitQuestion(val);
    input.value = '';
  }
}

// ── Legal Source / Form helpers ──
function showSources() {
  const cards = document.querySelectorAll('#screen-chat .legal-card');
  if (cards.length > 0) {
    cards.forEach(c => c.classList.add('open'));
    cards[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

async function generateForm() {
  const lastAI = [...chatMessages].reverse().find(m => m.type === 'ai' && m.intent);
  if (!lastAI) return;

  const intent = lastAI.intent.label || 'general';
  try {
    const r = await fetch('/forms');
    if (!r.ok) return;
    const data = await r.json();
    const forms = data.forms || [];
    const match = forms.find(f => f.includes(intent)) || forms[0];
    if (!match) return;

    const doc = { name: match.replace(/_/g, ' '), date: new Date().toLocaleDateString(), type: match };
    documents.push(doc);
  } catch (e) { /* silent */ }
}

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
  renderAll();
  switchTab('home');
});

// ── PWA ──
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}
