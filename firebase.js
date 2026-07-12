// Firebase SDK Import
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";

import {
    getAuth,
    GoogleAuthProvider,
    signInWithPopup,
    signOut,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";

import {
    getFirestore,
    collection,
    addDoc,
    getDocs,
    deleteDoc,
    doc
} from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";

import {
    getStorage
} from "https://www.gstatic.com/firebasejs/10.13.2/firebase-storage.js";


// Firebase Config

const firebaseConfig = {

  apiKey: "AIzaSyDgZ6oG1khblwfYpfhPWkwctbyQ2EjaSYk",

  authDomain: "ssc-easy-exam-for-tutor.firebaseapp.com",

  projectId: "ssc-easy-exam-for-tutor",

  storageBucket: "ssc-easy-exam-for-tutor.firebasestorage.app",

  messagingSenderId: "214421740095",

  appId: "1:214421740095:web:2f7215ecba69d3b241368a",

  measurementId: "G-4ZXR06LQVS"

};


// Initialize Firebase

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);

const db = getFirestore(app);

const storage = getStorage(app);

const provider = new GoogleAuthProvider();


// Developer Email

const ADMIN_EMAIL = "ahalim000155@gmail.com";


// Login Function

window.adminLogin = async function(){

    try{

        const result = await signInWithPopup(auth, provider);

        if(result.user.email===ADMIN_EMAIL){

            alert("Developer Login Successful");

        }else{

            alert("You are not Developer");

            await signOut(auth);

        }

    }

    catch(e){

        alert(e.message);

    }

}


// Login Check

onAuthStateChanged(auth,(user)=>{

    if(user){

        console.log(user.email);

    }

});