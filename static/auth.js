function togglePassword(id) {
  const input = document.getElementById(id);
  const icon = input.nextElementSibling.querySelector("i");

  if (input.type === "password") {
    input.type = "text";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  } else {
    input.type = "password";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const pwd = document.getElementById("password") || document.getElementById("signup-password");
  const strengthMeter = document.getElementById("strength-meter");

  if (pwd && strengthMeter) {
    pwd.addEventListener("input", () => {
      const val = pwd.value;
      let strength = "Слаба";
      let color = "#D74042";

      if (val.length >= 8 && /[A-Z]/.test(val) && /\d/.test(val)) {
        strength = "Силна";
        color = "#197C85";
      } else if (val.length >= 6) {
        strength = "Средна";
        color = "#F57426";
      }

      strengthMeter.textContent = `Сигурност: ${strength}`;
      strengthMeter.style.color = color;
    });
  }
});
