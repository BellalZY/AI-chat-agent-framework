
fetch('http://localhost:8000/api/ask/', {
  method: 'GET',
  credentials: 'include',
});


export const getAIMessage = async (userQuery) => {

  function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      let [key, value] = cookie.trim().split('=');
      if (key === name) return value;
    }
    return '';
  }

  const message = 
    {
      role: "assistant",
      content: "Connect your backend here...."
    }

  await fetch("http://localhost:8000/api/ask/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify({ "question": userQuery }),
    credentials: 'include',
  })
    .then(response => response.json())
    .then(data => {
      console.log(data)
      console.log("Answer:", data.answer);
      message.content = data.answer
    })
    .catch(error => {
      console.error("Error:", error);
    });

  return message;
};
