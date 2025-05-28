fetch("/api/status")
  .then(res => res.json())
  .then(data => {
    document.getElementById("status").innerText =
      `Устройство ${data.device}: ${data.status} (uptime: ${data.uptime})`;
  })
  .catch(err => {
    document.getElementById("status").innerText = "Ошибка подключения";
  });