document.getElementById('contact-form').addEventListener('submit', async function (event) {
    event.preventDefault();
  
    const formData = new FormData(this);
  
    const response = await fetch('/send-email', {
      method: 'POST',
      body: formData
    });
  
    if (response.ok) {
      alert('Email sent successfully!');
    } else {
      alert('Failed to send email.');
    }
  });
  