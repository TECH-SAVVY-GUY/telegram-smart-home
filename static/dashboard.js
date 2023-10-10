// Initialize Firebase
const firebaseConfig = {
    apiKey: "AIzaSyBf9zxQ4hhVlTFLwLbm1CJDxasipuOtsNo",
    authDomain: "telegram-smart-home.firebaseapp.com",
    databaseURL: "https://telegram-smart-home-default-rtdb.firebaseio.com",
    projectId: "telegram-smart-home",
    storageBucket: "telegram-smart-home.appspot.com",
    messagingSenderId: "612154709392",
    appId: "1:612154709392:web:17bd0c30cd5dde54150f15",
    measurementId: "G-N891QKRE9V",
};

firebase.initializeApp(firebaseConfig);

const database = firebase.database();

async function readData(path) {
    var dataRef = database.ref(path);
    try {
        var snapshot = await dataRef.once('value');
        var data = snapshot.val();
        return data;
    } catch (error) {
        console.error(error);
    }
}

var items = await readData('products/');

console.log(items);