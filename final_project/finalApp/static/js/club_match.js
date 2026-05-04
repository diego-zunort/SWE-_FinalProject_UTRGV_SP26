document.querySelectorAll(".match-action").forEach((button) => {
  button.addEventListener("click", () => {
    const status = document.querySelector(".match-status");
    if (!status) {
      return;
    }

    status.textContent = `${button.dataset.action} this recommendation`;
  });
});
