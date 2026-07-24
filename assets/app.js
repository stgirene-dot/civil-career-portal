const $ = (id) => document.getElementById(id);
const LOCATION_ORDER = ["Taiwan", "Singapore", "Hong Kong", "Japan", "South Korea", "Other Asia"];
const SCORE_WEIGHTS = {
  location: 0.30,
  technical: 0.30,
  skills: 0.20,
  level: 0.10,
  language: 0.05,
  company: 0.05
};
const favorites = new Set(JSON.parse(localStorage.getItem("careerFavorites") || "[]"));
let jobs = [];
let profile = localStorage.getItem("careerProfile") === "industry" ? "industry" : "academic";
let favoritesOnly = false;

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  })[char]);
}

function scoreFor(job) {
  const dimensions = job.scores?.[profile] || job.scores || {};
  return Math.round(Object.entries(SCORE_WEIGHTS).reduce(
    (total, [key, weight]) => total + (Number(dimensions[key]) || 0) * weight, 0
  ));
}

function normalizedSearch(job) {
  return [
    job.title, job.englishTitle, job.description, job.englishSummary, job.institution,
    job.location, job.country, job.category, ...(job.skills || []), ...(job.searchTerms || [])
  ].join(" ").toLocaleLowerCase();
}

function isNew(job) {
  if (typeof job.isNew === "boolean") return job.isNew;
  const date = new Date(`${job.firstSeen}T00:00:00Z`);
  return !Number.isNaN(date.valueOf()) && Date.now() - date.valueOf() <= 21 * 86400000;
}

function tag(text, className = "") {
  return `<span class="tag ${className}">${escapeHtml(text)}</span>`;
}

function scoreDetails(job) {
  const labels = {
    location: "Location", technical: "Research / technical", skills: "Skills",
    level: "Career level", language: "Language", company: "Company priority"
  };
  const dimensions = job.scores?.[profile] || {};
  return Object.keys(SCORE_WEIGHTS).map((key) =>
    `<li><span>${labels[key]}</span><strong>${Number(dimensions[key]) || 0}</strong></li>`
  ).join("");
}

function card(job) {
  const score = scoreFor(job);
  const englishAid = job.englishTitle && job.englishTitle !== job.title
    ? `<p class="english-title" lang="en">${escapeHtml(job.englishTitle)}</p>` : "";
  const summary = job.englishSummary
    ? `<p class="english-summary"><strong>English summary:</strong> ${escapeHtml(job.englishSummary)}</p>` : "";
  return `<article class="job-card">
    <div class="job-main">
      <div class="job-meta">
        ${tag(job.category, "category")}
        ${isNew(job) ? tag("NEW", "new") : ""}
        <span>${escapeHtml(job.location || job.country)}</span>
      </div>
      <h3 lang="${escapeHtml(job.language || "en")}">${escapeHtml(job.title)}</h3>
      ${englishAid}
      <p class="institution">${escapeHtml(job.institution)}</p>
      <p class="description" lang="${escapeHtml(job.language || "en")}">${escapeHtml(job.description)}</p>
      ${summary}
      <div class="skills">${(job.skills || []).map((skill) => tag(skill)).join("")}</div>
      <div class="actions">
        <a class="apply" href="${escapeHtml(job.url)}" target="_blank" rel="noopener noreferrer">View official posting <span aria-hidden="true">↗</span></a>
        <button class="favorite ${favorites.has(job.id) ? "on" : ""}" type="button" data-favorite="${escapeHtml(job.id)}" aria-pressed="${favorites.has(job.id)}" aria-label="${favorites.has(job.id) ? "Remove from" : "Add to"} favorites">★</button>
      </div>
    </div>
    <aside class="match-score">
      <div class="score-ring" style="--score:${score}" aria-label="${score} percent match"><strong>${score}</strong><span>% match</span></div>
      <details><summary>Score breakdown</summary><ul>${scoreDetails(job)}</ul></details>
    </aside>
  </article>`;
}

function render() {
  const query = $("search").value.trim().toLocaleLowerCase();
  const location = $("location").value;
  const category = $("category").value;
  const minimumScore = Number($("score").value);
  const rows = jobs.filter((job) =>
    (!query || normalizedSearch(job).includes(query)) &&
    (!location || job.country === location) &&
    (!category || job.category === category) &&
    scoreFor(job) >= minimumScore &&
    (!favoritesOnly || favorites.has(job.id))
  ).sort((a, b) =>
    scoreFor(b) - scoreFor(a) ||
    LOCATION_ORDER.indexOf(a.country) - LOCATION_ORDER.indexOf(b.country)
  );

  $("count").textContent = rows.length;
  $("saved").textContent = favorites.size;
  $("resultNote").textContent = favoritesOnly
    ? `Showing saved roles ranked for your ${profile} profile`
    : `Ranked for your ${profile} profile`;
  $("jobs").innerHTML = rows.map(card).join("") || `<div class="empty">
    <h3>No roles match these filters.</h3>
    <p>Try a broader keyword, location, or minimum score.</p>
  </div>`;
}

function setProfile(nextProfile) {
  profile = nextProfile;
  localStorage.setItem("careerProfile", profile);
  document.querySelectorAll("[data-profile]").forEach((button) => {
    const active = button.dataset.profile === profile;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  render();
}

function toggleFavorite(id) {
  favorites.has(id) ? favorites.delete(id) : favorites.add(id);
  localStorage.setItem("careerFavorites", JSON.stringify([...favorites]));
  render();
}

function populateLocations() {
  const available = new Set(jobs.map((job) => job.country));
  $("location").insertAdjacentHTML("beforeend", LOCATION_ORDER.filter((item) => available.has(item))
    .map((item) => `<option>${escapeHtml(item)}</option>`).join(""));
}

document.querySelectorAll("[data-profile]").forEach((button) =>
  button.addEventListener("click", () => setProfile(button.dataset.profile))
);
["search", "location", "category", "score"].forEach((id) => $(id).addEventListener("input", render));
$("favoritesOnly").addEventListener("click", () => {
  favoritesOnly = !favoritesOnly;
  $("favoritesOnly").classList.toggle("active", favoritesOnly);
  $("favoritesOnly").setAttribute("aria-pressed", String(favoritesOnly));
  render();
});
$("jobs").addEventListener("click", (event) => {
  const button = event.target.closest("[data-favorite]");
  if (button) toggleFavorite(button.dataset.favorite);
});

Promise.all([
  fetch("data/jobs.json", { cache: "no-store" }).then((response) => {
    if (!response.ok) throw new Error("Jobs data unavailable");
    return response.json();
  }),
  fetch("data/update-meta.json", { cache: "no-store" }).then((response) => response.json())
]).then(([jobData, meta]) => {
  jobs = jobData;
  populateLocations();
  $("updated").textContent = `Last updated ${meta.last_updated} · ${meta.sources_checked} official sources checked`;
  setProfile(profile);
}).catch(() => {
  $("updated").textContent = "Update time unavailable";
  $("jobs").innerHTML = '<div class="empty"><h3>Job data could not be loaded.</h3><p>Open this portal through its web address rather than as a local file.</p></div>';
});
