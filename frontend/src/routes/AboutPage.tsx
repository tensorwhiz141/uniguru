
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useAuth } from "../context/AuthContext";
import { faChevronLeft } from "@fortawesome/free-solid-svg-icons";
import uniguru from "../assets/uni-logo.png";
import i18n from "../i18n";
// import StarsCanvas from "../components/StarBackground";

const AboutPage = () => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();
  const L = (en: string, hi: string, mr: string) => (i18n.language === 'hi' ? hi : i18n.language === 'mr' ? mr : en);

  return (
    <div className="relative min-h-screen text-white">
      {/* Mobile Back Button - Only visible on mobile */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center justify-center w-10 h-10 bg-black/50 backdrop-blur-sm border border-white/20 rounded-full text-white hover:bg-black/70 transition-all duration-200 shadow-lg"
          aria-label={L('Go back','वापस जाएँ','मागे जा')}
        >
          <FontAwesomeIcon icon={faChevronLeft} className="text-lg" />
        </button>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12 max-w-4xl">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <img
              src={uniguru}
              alt="UniGuru Logo"
              className="w-16 h-16 object-contain mr-4"
            />
            <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent"
                style={{
                  background: "linear-gradient(135deg, #b18615, #d4a01c, #f7c52d, #d4a01c, #b18615)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text"
                }}>
              {L('About UniGuru','UniGuru के बारे में','UniGuru विषयी')}
            </h1>
          </div>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            {L('Your intelligent academic companion powered by advanced AI technology','आपका बुद्धिमान अकादमिक साथी, उन्नत एआई तकनीक द्वारा संचालित','तुमचा बुद्धिमान शैक्षणिक साथी, प्रगत एआय तंत्रज्ञानाने समर्थित')}
          </p>
        </div>

        {/* Mission Section */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold mb-6 text-center bg-clip-text text-transparent"
              style={{
                background: "linear-gradient(135deg, #b18615, #d4a01c, #f7c52d, #d4a01c, #b18615)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text"
              }}>
            {L('Our Mission','हमारा मिशन','आमचे ध्येय')}
          </h2>
          <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-8 border border-gray-700">
            <p className="text-lg text-gray-300 leading-relaxed text-center">
              {L('UniGuru is designed to revolutionize the way students learn and interact with educational content. We provide personalized AI tutoring that adapts to your learning style, helping you achieve academic excellence through intelligent conversations and comprehensive support.',
                 'UniGuru छात्रों के सीखने और शैक्षिक सामग्री के साथ बातचीत करने के तरीके को बदलने के लिए बनाया गया है। हम व्यक्तिगत एआई ट्यूटरिंग प्रदान करते हैं जो आपकी सीखने की शैली के अनुकूल होती है, जिससे आप बुद्धिमान वार्तालापों और व्यापक सहायता के माध्यम से शैक्षणिक उत्कृष्टता प्राप्त कर सकें।',
                 'UniGuru विद्यार्थी कसे शिकतात आणि शैक्षणिक सामग्रीशी संवाद साधतात ते बदलण्यासाठी डिझाइन केले आहे. आम्ही वैयक्तिकृत एआय ट्युट���िंग प्रदान करतो जे तुमच्या शिकण्याच्या शैलीशी जुळते, त्यामुळे तुम्ही बुद्धिमान संभाषण आणि सर्वसमावेशक सहाय्याद्वारे शैक्षणिक उत्कृष्टता साध्य करू शकता.')}
            </p>
          </div>
        </div>

        {/* Features Section */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-yellow-400 to-yellow-600 bg-clip-text text-transparent">
            {L('Key Features','मुख्य विशेषताएँ','मुख्य वैशिष्ट्ये')}
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-yellow-400/50 transition-colors">
              <h3 className="text-xl font-semibold mb-3 text-yellow-400">🤖 {L('AI-Powered Tutoring','एआई-संचालित ट्यूटोरिंग','एआय-चालित ट्युटरिंग')}</h3>
              <p className="text-gray-300">
                {L('Get personalized help with your studies through our advanced AI that understands your learning needs.','हमारे उन्नत एआई के माध्यम से अपनी पढ़ाई में व्यक्तिगत मदद प्राप्त करें जो आपकी सीखने की आवश्यकताओं को समझता है।','आमच्या प्रगत एआयद्वारे तुमच्या अभ्यासासाठी वैयक्तिक मदत मिळवा जो तुमच्या शिकण्याच्या गरजा समजतो.')}
              </p>
            </div>
            <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-yellow-400/50 transition-colors">
              <h3 className="text-xl font-semibold mb-3 text-yellow-400">📚 {L('Multi-Subject Support','बहु-विषयक सहायता','बहु-विषयक समर्थन')}</h3>
              <p className="text-gray-300">
                {L('From mathematics to literature, our AI covers a wide range of academic subjects and topics.','गणित से साहित्य तक, हमारा एआई कई शैक्षणिक विषयों और टॉपिक्स को कवर करता है।','गणितापासून साहित्यापर्यंत, आमचा एआय विविध शैक्षणिक विषय आणि विषयांवर कव्हर करतो.')}
              </p>
            </div>
            <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-yellow-400/50 transition-colors">
              <h3 className="text-xl font-semibold mb-3 text-yellow-400">💬 {L('Interactive Conversations','इ��टरैक्टिव बातचीत','परस्परसंवादी संभाषणे')}</h3>
              <p className="text-gray-300">
                {L('Engage in natural conversations with your AI tutor, ask questions, and get detailed explanations.','अपने एआई ट्यूटर के साथ स्वाभाविक बातचीत करें, प्रश्न पूछें और विस्तृत स्पष्टीकरण प्राप्त करें।','तुमच्या एआय ट्यूटरसोबत नैसर्गिक संभाषणे करा, प्रश्न विचारा आणि सविस्तर स्पष्टीकरणे मिळवा.')}
              </p>
            </div>
            <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-yellow-400/50 transition-colors">
              <h3 className="text-xl font-semibold mb-3 text-yellow-400">📊 {L('Progress Tracking','प्रगति ट्रैकिंग','प्रगती ट्रॅकिंग')}</h3>
              <p className="text-gray-300">
                {L('Monitor your learning progress and get insights into your academic development over time.','अपनी सीखने की प्रगति की निगरानी करें और समय के साथ आपके शैक्षणिक विकास की अंतर्दृष्टि प्राप्त करें।','तुमच्या शिकण्याच्या प्रगतीचे निरीक्षण करा आणि कालांतराने तुमच्या शैक्षणिक विकासाबद्दल अंतर्दृष्टी मिळवा.')}
              </p>
            </div>
          </div>
        </div>

        {/* Technology Section */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold mb-6 text-center bg-clip-text text-transparent"
              style={{
                background: "linear-gradient(135deg, #b18615, #d4a01c, #f7c52d, #d4a01c, #b18615)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text"
              }}>
            {L('Technology','प्रौद्योगिकी','तंत्रज्ञान')}
          </h2>
          <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-8 border border-gray-700">
            <p className="text-lg text-gray-300 leading-relaxed text-center mb-6">
              {L('UniGuru leverages cutting-edge artificial intelligence and natural language processing to provide you with the most effective learning experience possible.',
                 'UniGuru अत्याधुनिक कृत्रिम बुद्धिमत्ता और प्राकृतिक भाषा प्रसंस्करण का उपयोग करता है ताकि आपको सबसे प्रभावी सीखने का अनुभव मिल सके।',
                 'UniGuru अत्याधुनिक कृत्रिम बुद्धिमत्तेचा आणि नैसर्गिक भाषा प्रक्रिया चा वापर करून तुम्हाला सर्वात प्रभावी शिकण्याचा अनुभव देतो.')}
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <span className="px-4 py-2 bg-gray-800/80 border border-gray-600 rounded-full text-sm font-medium text-yellow-400">
                {L('Machine Learning','मशीन लर्निंग','मशीन लर्निंग')}
              </span>
              <span className="px-4 py-2 bg-gray-800/80 border border-gray-600 rounded-full text-sm font-medium text-yellow-400">
                {L('Natural Language Processing','नेचुरल लैंग्वेज प्रोसेसिंग','नॅचरल ल��ग्वेज प्रोसेसिंग')}
              </span>
              <span className="px-4 py-2 bg-gray-800/80 border border-gray-600 rounded-full text-sm font-medium text-yellow-400">
                {L('Adaptive Learning','एडेप्टिव लर्निंग','ऍडॅप्टिव लर्निंग')}
              </span>
              <span className="px-4 py-2 bg-gray-800/80 border border-gray-600 rounded-full text-sm font-medium text-yellow-400">
                {L('Real-time Analysis','रीयल-टाइम विश्लेषण','रिअल-टाइम विश्लेषण')}
              </span>
            </div>
          </div>
        </div>

        {/* Contact Section */}
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-6 bg-clip-text text-transparent"
              style={{
                background: "linear-gradient(135deg, #b18615, #d4a01c, #f7c52d, #d4a01c, #b18615)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text"
              }}>
            {L('Get Started Today','आज ही शुरू करें','आजच सुरू करा')}
          </h2>
          <p className="text-lg text-gray-300 mb-8">
            {L('Ready to enhance your learning experience? Join thousands of students who are already using UniGuru.',
               'क्या आप अपने सीखने के अनुभव को बेहतर बनाने के लिए तैयार हैं? उन हजारों छात्रों से जुड़ें जो पहले से ही UniGuru का उपयोग कर रहे हैं।',
               'तुमचा शिकण्याचा अनुभव सुधारण्यासाठी तयार आहात का? UniGuru आधीच वापरत असलेल्या हजारो विद्यार्थ्यांमध्ये सामील व्हा.')}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => window.location.href = '/signup'}
              className="px-8 py-3 bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-semibold rounded-full hover:from-yellow-300 hover:to-yellow-500 transition-all duration-200 transform hover:scale-105 shadow-lg"
            >
              {L('Sign Up Now','अभी साइन अप करें','आता साइन अप करा')}
            </button>
            <button
              onClick={() => navigate(isLoggedIn ? '/chatpage' : '/login')}
              className="px-8 py-3 border-2 border-yellow-400 text-yellow-400 font-semibold rounded-full hover:bg-yellow-400 hover:text-black transition-all duration-200 transform hover:scale-105"
            >
              {L('Try Demo','डेमो आज़माएं','डेमो वापरा')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
