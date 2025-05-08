// Simulated data source
const clubData = {
    name: "Tech Society",
    image: "img/tech-club.jpg",
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
  };
  
  // DOM Population
  window.onload = () => {
    document.getElementById("club-name").textContent = clubData.name;
    document.getElementById("club-image").src = clubData.image;
    document.getElementById("club-description").textContent = clubData.description;
    document.getElementById("club-mission").textContent = clubData.mission;
    document.getElementById("club-admin").textContent = clubData.admin;
  
    const eventsList = document.getElementById("club-events");
    clubData.events.forEach(event => {
      const li = document.createElement("li");
      li.textContent = event;
      eventsList.appendChild(li);
    });
  
    const gallery = document.getElementById("club-gallery");
    clubData.gallery.forEach(media => {
      const el = document.createElement(media.type === "video" ? "video" : "img");
      el.src = media.src;
      if (media.type === "video") el.controls = true;
      gallery.appendChild(el);
    });
  
    const resourcesList = document.getElementById("club-resources");
    clubData.resources.forEach(resource => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = resource.link;
      a.textContent = resource.name;
      a.target = "_blank";
      li.appendChild(a);
      resourcesList.appendChild(li);
    });
  
    // Join button toggle
    const joinBtn = document.getElementById("join-btn");
    joinBtn.addEventListener("click", () => {
      joinBtn.classList.toggle("joined");
      joinBtn.textContent = joinBtn.classList.contains("joined") ? "Joined" : "Join";
    });
  };
  