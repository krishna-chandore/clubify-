function toggleFollow(button) {
    if (button.innerText === "Follow") {
      button.innerText = "Following";
      button.style.backgroundColor = "#ccc";
    } else {
      button.innerText = "Follow";
      button.style.backgroundColor = "#21c41b";
    }
  }
  