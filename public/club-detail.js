// club-detail.js

// Simulated club data
const clubDatabase = {
  tech: {
    name: "Manas club",
    image: "..\src\manas club.png",
    description: "The Tech Society promotes innovation through tech workshops, hackathons, and seminars.",
    mission: "To empower students with the latest in technology and foster a creative problem-solving environment.",
    events: ["AI Hackathon", "Web3 Seminar", "Robotics Bootcamp"],
    gallery: [
      { type: "image", src: "img/event1.jpg" },
      { type: "video", src: "video/highlights.mp4" },
      { type: "image", src: "img/event2.jpg" }
    ],
    resources: [
      { name: "Workshop Slides", link: "resources/slides.pdf" },
      { name: "Hackathon Guide", link: "resources/guide.pdf" }
    ],
    admin: "John Doe, President (john@college.edu)"
  },
  art: {
    name: "Art Circle",
    image: "img/art-club.jpg",
    description: "A haven for budding artists and creatives.",
    mission: "To cultivate artistic expression and appreciation among students.",
    events: ["Sketch Jam", "Gallery Night", "Mural Week"],
    gallery: [
      { type: "image", src: "img/art1.jpg" },
      { type: "image", src: "img/art2.jpg" }
    ],
    resources: [
      { name: "Color Theory Guide", link: "resources/art-guide.pdf" }
    ],
    admin: "Ella Stone, Coordinator (ella@college.edu)"
  },
  music: {
    name: "Music Ensemble",
    image: "img/music-club.jpg",
    description: "For students passionate about creating and performing music.",
    mission: "To bring students together through the joy of music.",
    events: ["Open Mic Night", "Fusion Fest", "Acoustic Jam"],
    gallery: [
      { type: "video", src: "video/music1.mp4" },
      { type: "image", src: "img/music2.jpg" }
    ],
    resources: [
      { name: "Sheet Music Collection", link: "resources/sheet-music.pdf" }
    ],
    admin: "Mike Jensen, Head (mike@college.edu)"
  }
};

// Utility to get query parameter
function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

// DOM Population
window.onload = () => {
  const clubKey = getQueryParam("club");
  const clubData = clubDatabase[clubKey];

  if (!clubData) {
    alert("Club not found!");
    return;
  }

  document.getElementById("club-name").textContent = clubData.name;
  document.getElementById("club-image").src = clubData.image;
  document.getElementById("club-description").textContent = clubData.description;
  document.getElementById("club-mission").textContent = clubData.mission;
  document.getElementById("club-admin").textContent = clubData.admin;

  const eventsList = document.getElementById("club-events");
  eventsList.innerHTML = "";
  clubData.events.forEach(event => {
    const li = document.createElement("li");
    li.textContent = event;
    eventsList.appendChild(li);
  });

  const gallery = document.getElementById("club-gallery");
  gallery.innerHTML = "";
  clubData.gallery.forEach(media => {
    const el = document.createElement(media.type === "video" ? "video" : "img");
    el.src = media.src;
    if (media.type === "video") el.controls = true;
    gallery.appendChild(el);
  });

  const resourcesList = document.getElementById("club-resources");
  resourcesList.innerHTML = "";
  clubData.resources.forEach(resource => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = resource.link;
    a.textContent = resource.name;
    a.target = "_blank";
    li.appendChild(a);
    resourcesList.appendChild(li);
  });

  // Join button
  const joinBtn = document.getElementById("join-btn");
  joinBtn.addEventListener("click", () => {
    joinBtn.classList.toggle("joined");
    joinBtn.textContent = joinBtn.classList.contains("joined") ? "Joined" : "Join";
  });
};
