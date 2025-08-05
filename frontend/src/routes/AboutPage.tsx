import React from "react";
import uniguru from "../assets/uni-logo.png";
// import StarsCanvas from "../components/StarBackground";

const AboutPage: React.FC = () => {
  return (
    <div className="relative min-h-screen text-white">
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
              About UniGuru
            </h1>
          </div>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Your intelligent academic companion powered by advanced AI technology
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
            Our Mission
          </h2>
          <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-8 border border-gray-700">
            <p className="text-lg text-gray-300 leading-relaxed text-center">
              UniGuru is designed to revolutionize the way students learn and interact with educational content.
              We provide personalized AI tutoring that adapts to your learning style, helping you achieve
              academic excellence through intelligent conversations and comprehensive support.
            </p>
          </div>
        </div>

        {/* Features Section */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-yellow-400 to-yellow-600 bg-clip-text text-transparent">
            Key Features
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-yellow-400/50 transition-colors">
              <h3 className="text-xl font-semibold mb-3 text-yellow-400">🤖 AI-Powered Tutoring</h3>
              <p className="text-gray-300">
                Get personalized help with your studies through our advanced AI that understands your learning needs.
              </p>
            </div>
            <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-yellow-400/50 transition-colors">
              <h3 className="text-xl font-semibold mb-3 text-yellow-400">📚 Multi-Subject Support</h3>
              <p className="text-gray-300">
                From mathematics to literature, our AI covers a wide range of academic subjects and topics.
              </p>
            </div>
            <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-yellow-400/50 transition-colors">
              <h3 className="text-xl font-semibold mb-3 text-yellow-400">💬 Interactive Conversations</h3>
              <p className="text-gray-300">
                Engage in natural conversations with your AI tutor, ask questions, and get detailed explanations.
              </p>
            </div>
            <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-yellow-400/50 transition-colors">
              <h3 className="text-xl font-semibold mb-3 text-yellow-400">📊 Progress Tracking</h3>
              <p className="text-gray-300">
                Monitor your learning progress and get insights into your academic development over time.
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
            Technology
          </h2>
          <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-8 border border-gray-700">
            <p className="text-lg text-gray-300 leading-relaxed text-center mb-6">
              UniGuru leverages cutting-edge artificial intelligence and natural language processing
              to provide you with the most effective learning experience possible.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <span className="px-4 py-2 bg-gray-800/80 border border-gray-600 rounded-full text-sm font-medium text-yellow-400">
                Machine Learning
              </span>
              <span className="px-4 py-2 bg-gray-800/80 border border-gray-600 rounded-full text-sm font-medium text-yellow-400">
                Natural Language Processing
              </span>
              <span className="px-4 py-2 bg-gray-800/80 border border-gray-600 rounded-full text-sm font-medium text-yellow-400">
                Adaptive Learning
              </span>
              <span className="px-4 py-2 bg-gray-800/80 border border-gray-600 rounded-full text-sm font-medium text-yellow-400">
                Real-time Analysis
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
            Get Started Today
          </h2>
          <p className="text-lg text-gray-300 mb-8">
            Ready to enhance your learning experience? Join thousands of students who are already using UniGuru.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => window.location.href = '/signup'}
              className="px-8 py-3 bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-semibold rounded-full hover:from-yellow-300 hover:to-yellow-500 transition-all duration-200 transform hover:scale-105 shadow-lg"
            >
              Sign Up Now
            </button>
            <button
              onClick={() => window.location.href = '/chatpage'}
              className="px-8 py-3 border-2 border-yellow-400 text-yellow-400 font-semibold rounded-full hover:bg-yellow-400 hover:text-black transition-all duration-200 transform hover:scale-105"
            >
              Try Demo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
