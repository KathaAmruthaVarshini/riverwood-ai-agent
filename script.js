const API_URL = "https://riverwood-ai-agent.onrender.com"; // Your deployed backend URL
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const voiceBtn = document.getElementById("voice-btn");

function addMessage(sender, text) {
  const msg = document.createElement("div");
  msg.textContent = `${sender}: ${text}`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;
  addMessage("🧑 You", message);
  userInput.value = "";

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    const reply = data.reply || "Sorry, I didn’t understand that.";
    addMessage("🤖 Riverwood AI", reply);
    speakText(reply);
  } catch (error) {
    addMessage("❌ Error", "Unable to connect to backend");
    console.error(error);
  }
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

function speakText(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-IN"; // Change to "hi-IN" for Hindi
  speechSynthesis.speak(utterance);
}

voiceBtn.addEventListener("click", () => {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "en-IN"; // or "hi-IN" for Hindi
  recognition.start();

  recognition.onresult = (event) => {
    const voiceText = event.results[0][0].transcript;
    userInput.value = voiceText;
    sendMessage();
  };
});
