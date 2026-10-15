const grid = document.querySelector("#city-grid");
const empty = document.querySelector("#empty-state");
const message = document.querySelector("#message");
const form = document.querySelector("#city-form");
const input = document.querySelector("#city-input");
const addButton = document.querySelector("#add-button");

const weatherIcon = code => code === 0 ? "☀" : code <= 3 ? "⛅" : code <= 67 ? "🌧" : code <= 77 ? "❄" : code <= 82 ? "🌦" : "⛈";
const escapeHtml = value => String(value ?? "").replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[char]));

function showMessage(text, isError=false){ message.textContent=text; message.className=`message${isError ? " error" : ""}`; }
async function request(url, options={}){
  const response=await fetch(url, options); const data=await response.json();
  if(!response.ok) throw new Error(data.error || "Something went wrong."); return data;
}
function card(city){
  const w=city.weather;
  return `<article class="city-card" data-id="${city.id}">
    <div class="city-top"><div><h3 class="city-name">${escapeHtml(city.name)}</h3><div class="country">${escapeHtml(city.country)}</div></div><button class="remove" data-remove="${city.id}" aria-label="Remove ${escapeHtml(city.name)}">×</button></div>
    ${w ? `<div class="weather-main"><span class="temp">${Math.round(w.temperature_c)}°</span><span class="weather-icon" aria-hidden="true">${weatherIcon(w.weather_code)}</span></div>
      <div class="details"><div><span class="detail-label">Wind speed</span><strong>${w.windspeed_kmh ?? "—"} km/h</strong></div><div><span class="detail-label">Coordinates</span><strong>${city.latitude.toFixed(2)}, ${city.longitude.toFixed(2)}</strong></div></div>
      <span class="source"><span class="source-dot"></span>${escapeHtml(w.source)} · ${new Date(w.fetched_at).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}</span>`
      : `<div class="weather-main"><span class="temp">—°</span><span class="weather-icon">◌</span></div><div class="details"><span class="detail-label">Fetching latest weather…</span></div>`}
  </article>`;
}
async function loadCities(fetchWeather=true){
  grid.innerHTML='<div class="city-card skeleton"></div><div class="city-card skeleton"></div><div class="city-card skeleton"></div>';
  try{
    let cities=await request("/cities");
    if(fetchWeather) cities=await Promise.all(cities.map(async c => { try{return await request(`/cities/${encodeURIComponent(c.name)}/weather`)}catch{return c} }));
    grid.innerHTML=cities.map(card).join(""); empty.hidden=cities.length>0;
  }catch(error){grid.innerHTML=""; empty.hidden=false; showMessage(error.message,true)}
}
form.addEventListener("submit",async event=>{event.preventDefault();addButton.disabled=true;showMessage("Finding and saving your city…");try{const data=await request("/cities",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:input.value})});input.value="";showMessage(data.message);await loadCities()}catch(error){showMessage(error.message,true)}finally{addButton.disabled=false}});
grid.addEventListener("click",async event=>{const id=event.target.dataset.remove;if(!id)return;if(!confirm("Remove this city and its saved readings?"))return;try{await request(`/cities/${id}`,{method:"DELETE"});showMessage("City removed.");await loadCities(false)}catch(error){showMessage(error.message,true)}});
document.querySelector("#refresh-all").addEventListener("click",()=>loadCities(true));
loadCities(true);
