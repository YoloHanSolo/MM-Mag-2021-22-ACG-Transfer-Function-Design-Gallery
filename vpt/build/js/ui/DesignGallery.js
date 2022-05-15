import { UIObject } from './UIObject.js';

const response = await fetch('./html/ui/DesignGallery.html');
const template = await response.text();

export class DesignGallery extends UIObject {

constructor(options) {
    super(template, options);

    this._binds.generateRandom.addEventListener('click', e => {
        console.log("apply")
    });

    this._binds.explore.addEventListener('click', e => {
        console.log("apply")
    });

    this._binds.apply.addEventListener('click', e => {
        console.log("apply")
    });
}

generateRandomTF() {
    fetch('http://localhost:5000/generate-random-tf', {
        method: "GET",
        headers: {'Content-Type': 'application/json'}, 
        body: null
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        //this._updateDesignGallery(data)
    });
}

exploreTF() {
    fetch('http://localhost:5000/explore-tf', {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({"key": "value"})
    })
    .then(response => response.json())
    .then(data => {
        this._updateDesignGallery(data)
    });
}

applyTF() {
    console.log("HEHE");
    this.trigger('change');
}

_updateDesignGallery(data) {

    /*
    for (const transferFunction of data.transfer_functions) {
        const id = transferFunction.name;
        const value =  transferFunction.value;
        document.getElementById(id).innerText = value
    }
    */
}


}