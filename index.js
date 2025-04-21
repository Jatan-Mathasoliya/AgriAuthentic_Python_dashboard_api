const sugge = {
    "pH": "Maintain it",
    "Moisture": "Add or remove Water",
}

let array = [];

let failuer = [
    "pH",
    "Moisture",
]
for(i=0; i<failuer.length; i++){
    array.append(sugge[failuer[1]]);
    // console.log(failuer[i])
}
console.log(array)