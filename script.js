// ==========================
// Question Bank Script
// ==========================

// Subject Card

const cards = document.querySelectorAll(".subject-card");

const main = document.querySelector("main");

const questionPage = document.getElementById("questionPage");

const subjectTitle = document.getElementById("subjectTitle");

const backBtn = document.getElementById("backBtn");

// Search

const searchInput = document.getElementById("searchInput");

// Dark Mode

const themeBtn = document.getElementById("themeBtn");

// Admin

const adminBtn = document.getElementById("adminBtn");

const adminModal = document.getElementById("adminModal");

const loginBtn = document.getElementById("loginBtn");

// ==========================
// Open Subject
// ==========================

cards.forEach(card=>{

card.onclick=function(){

subjectTitle.innerHTML=this.dataset.subject;

main.style.display="none";

questionPage.classList.remove("hidden");

};

});

// ==========================
// Back Button
// ==========================

backBtn.onclick=function(){

questionPage.classList.add("hidden");

main.style.display="grid";

};

// ==========================
// Search
// ==========================

searchInput.onkeyup=function(){

let value=this.value.toLowerCase();

cards.forEach(card=>{

card.style.display=

card.innerText.toLowerCase().includes(value)

?

"block"

:

"none";

});

};

// ==========================
// Dark Mode
// ==========================

themeBtn.onclick=function(){

document.body.classList.toggle("dark");

};

// ==========================
// Admin Popup
// ==========================

adminBtn.onclick=function(){

adminModal.classList.remove("hidden");

};

// Close Modal

window.onclick=function(e){

if(e.target==adminModal){

adminModal.classList.add("hidden");

}

};

// ==========================
// Login Button
// ==========================

loginBtn.onclick=function(){

alert("Firebase Login will be connected in next step.");

};