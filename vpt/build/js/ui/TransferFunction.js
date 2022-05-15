import { UIObject } from './UIObject.js';

import { DOMUtils } from '../utils/DOMUtils.js';
import { CommonUtils } from '../utils/CommonUtils.js';
import { WebGL } from '../WebGL.js';
import { Draggable } from '../Draggable.js';

const [ SHADERS, MIXINS ] = await Promise.all([
    'shaders.json',
    'mixins.json',
].map(url => fetch(url).then(response => response.json())));

const [ template, templateBump ] = await Promise.all([
    './html/ui/TransferFunction.html',
    './html/ui/TransferFunctionBump.html',
].map(url => fetch(url).then(response => response.text())));

export class TransferFunction extends UIObject {

constructor(options) {
    super(template, options);

    this._onColorChange = this._onColorChange.bind(this);

    Object.assign(this, {
        _width                  : 256,
        _height                 : 256,
        _transferFunctionWidth  : 256,
        _transferFunctionHeight : 256,
        scaleSpeed              : 0.003
    }, options);

    this._canvas = this._element.querySelector('canvas');
    this._canvas.width = this._transferFunctionWidth;
    this._canvas.height = this._transferFunctionHeight;
    this.resize(this._width, this._height);

    this._gl = this._canvas.getContext('webgl2', {
        depth                 : false,
        stencil               : false,
        antialias             : false,
        preserveDrawingBuffer : true
    });
    const gl = this._gl;

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

    this._clipQuad = WebGL.createClipQuad(gl);
    this._program = WebGL.buildPrograms(gl, {
        TransferFunction: SHADERS.TransferFunction
    }, MIXINS).TransferFunction;
    const program = this._program;
    gl.useProgram(program.program);
    gl.bindBuffer(gl.ARRAY_BUFFER, this._clipQuad);
    gl.enableVertexAttribArray(program.attributes.aPosition);
    gl.vertexAttribPointer(program.attributes.aPosition, 2, gl.FLOAT, false, 0, 0);

    this._bumps = [];
    this._binds.addBump.addEventListener('click', e => {
        this.addBump();
    });
    this._binds.removeSelectedBump.addEventListener('click', e => {
        this.removeSelectedBump();
    });
    this._binds.removeAllBumps.addEventListener('click', e => {
        this.removeAllBumps();
    });

    this._binds.color.addEventListener('change', this._onColorChange);
    this._binds.alpha.addEventListener('change', this._onColorChange);

    this._binds.load.addEventListener('click', e => {
        CommonUtils.readTextFile(data => {
            this._bumps = JSON.parse(data);
            this.render();
            this._rebuildHandles();
            this.trigger('change');
        });
    });

    this._binds.save.addEventListener('click', e => {
        CommonUtils.downloadJSON(this._bumps, 'TransferFunction.json');
    });

    this._designGallery = null;
    this._indexTF = -1;

    this._binds.generateTransferFunctionGallery.addEventListener('click', e => {
        this.loadingPreviews();
        const filename = document.getElementById("filename").innerText;
        fetch('http://localhost:5000/random-tf', {
            method: "POST",
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify({
                filename: filename
            })
        })
        .then(response => response.json())
        .then(data => {
            this._loadState = 'loaded';
            this._designGallery = data;
            this.updatePreviews();
        });    
    });

    this._binds.exploreSelectedTransferFunction.addEventListener('click', e => {
        this.loadingPreviews();
        const filename = document.getElementById("filename").innerText;
        fetch('http://localhost:5000/explore-tf', {
            method: "POST",
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify({
                filename: filename,
                feature_vector: this._designGallery[this._indexTF].feature_vector
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            this._designGallery = data;
            this.updatePreviews();
        });      
    });

    this._binds.tf0.addEventListener('click', e => {
        this._bumps = this._designGallery[0].transfer_function;
        this._indexTF = 0;
        this.render();
        this._rebuildHandles();
        this.trigger('change');  
    });

    this._binds.tf1.addEventListener('click', e => {
        this._bumps = this._designGallery[1].transfer_function;
        this._indexTF = 1;
        this.render();
        this._rebuildHandles();
        this.trigger('change');  
    });

    this._binds.tf2.addEventListener('click', e => {
        this._bumps = this._designGallery[2].transfer_function;
        this._indexTF = 2;
        this.render();
        this._rebuildHandles();
        this.trigger('change');  
    });

    this._binds.tf3.addEventListener('click', e => {
        this._bumps = this._designGallery[3].transfer_function;
        this._indexTF = 3;
        this.render();
        this._rebuildHandles();
        this.trigger('change');  
    });

    this._binds.tf4.addEventListener('click', e => {
        this._bumps = this._designGallery[4].transfer_function;
        this._indexTF = 4;
        this.render();
        this._rebuildHandles();
        this.trigger('change');  
    });

    this._binds.tf5.addEventListener('click', e => {
        this._bumps = this._designGallery[5].transfer_function;
        this._indexTF = 5;
        this.render();
        this._rebuildHandles();
        this.trigger('change');  
    });

    this._binds.tf6.addEventListener('click', e => {
        this._bumps = this._designGallery[6].transfer_function;
        this._indexTF = 6;
        this.render();
        this._rebuildHandles();
        this.trigger('change');  
    });

    this._binds.tf7.addEventListener('click', e => {
        this._bumps = this._designGallery[7].transfer_function;
        this._indexTF = 7;
        this.render();
        this._rebuildHandles();
        this.trigger('change');  
    });

    this._binds.tf8.addEventListener('click', e => {
        this._bumps = this._designGallery[8].transfer_function;
        this._indexTF = 8;
        this.render();
        this._rebuildHandles();
        this.trigger('change');  
    });

}

updatePreviews() {
    for (let i = 0; i < 9; i++) {
        document.getElementById("tf" + i).src = "http://localhost:5000/preview-tf/" + i + "?" + Math.random(); // random to hack caching
    }
}

loadingPreviews() {
    for (let i = 0; i < 9; i++) {
        document.getElementById("tf" + i).src = "https://www.wpfaster.org/wp-content/uploads/2013/06/circle-loading-gif.gif";
    }
}

destroy() {
    const gl = this._gl;
    gl.deleteBuffer(this._clipQuad);
    gl.deleteProgram(this._program.program);
    this._element.remove();
}

resize(width, height) {
    this._canvas.style.width = width + 'px';
    this._canvas.style.height = height + 'px';
    this._width = width;
    this._height = height;
}

resizeTransferFunction(width, height) {
    this._canvas.width = width;
    this._canvas.height = height;
    this._transferFunctionWidth = width;
    this._transferFunctionHeight = height;
    const gl = this._gl;
    gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
}

render() {
    const gl = this._gl;
    const { uniforms } = this._program;

    gl.clear(gl.COLOR_BUFFER_BIT);
    for (const bump of this._bumps) {
        gl.uniform2f(uniforms.uPosition, bump.position.x, bump.position.y);
        gl.uniform2f(uniforms.uSize, bump.size.x, bump.size.y);
        gl.uniform4f(uniforms.uColor, bump.color.r, bump.color.g, bump.color.b, bump.color.a);
        gl.drawArrays(gl.TRIANGLE_FAN, 0, 4);
    }
}

getValue() {
    return this._canvas;
}

addBump(options) {
    const bumpIndex = this._bumps.length;
    const newBump = {
        position: {
            x: 0.5,
            y: 0.5,
        },
        size: {
            x: 0.2,
            y: 0.2,
        },
        color: {
            r: 1,
            g: 0,
            b: 0,
            a: 1,
        },
    };
    this._bumps.push(newBump);
    this._addHandle(bumpIndex);
    this.selectBump(bumpIndex);
    this.render();
    this.trigger('change');
}

removeSelectedBump() {
    this._removeHandle(this.getSelectedBumpIndex());
}

removeAllBumps() {
    this._bumps = [];
    this._rebuildHandles();
    this.render();
    this.trigger('change');
}

_removeHandle(index) {
    const handles = this._element.querySelectorAll('.bump');
    for (const handle of handles) {
        const handleIndex = parseInt(handle.dataset.index);
        if (handleIndex === index) {
            this._bumps.splice(handleIndex, 1);
        }
    }
    this._rebuildHandles();
    this.render();
    this.trigger('change');
}

_addHandle(index) {
    const handle = DOMUtils.instantiate(templateBump);
    this._element.querySelector('.widget').appendChild(handle);
    handle.dataset.index = index;

    const left = this._bumps[index].position.x * this._width;
    const top = (1 - this._bumps[index].position.y) * this._height;
    handle.style.left = Math.round(left) + 'px';
    handle.style.top = Math.round(top) + 'px';

    new Draggable(handle, handle.querySelector('.bump-handle'));
    handle.addEventListener('draggable', e => {
        const x = e.currentTarget.offsetLeft / this._width;
        const y = 1 - (e.currentTarget.offsetTop / this._height);
        const i = parseInt(e.currentTarget.dataset.index);
        this._bumps[i].position.x = x;
        this._bumps[i].position.y = y;
        this.render();
        this.trigger('change');
    });
    handle.addEventListener('pointerdown', e => {
        const i = parseInt(e.currentTarget.dataset.index);
        this.selectBump(i);
    });
    handle.addEventListener('wheel', e => {
        const amount = e.deltaY * this.scaleSpeed;
        const scale = Math.exp(-amount);
        const i = parseInt(e.currentTarget.dataset.index);
        this.selectBump(i);
        if (e.shiftKey) {
            this._bumps[i].size.y *= scale;
        } else {
            this._bumps[i].size.x *= scale;
        }
        this.render();
        this.trigger('change');
    });
}

_rebuildHandles() {
    const handles = this._element.querySelectorAll('.bump');
    for (const handle of handles) {
        handle.remove();
    }
    for (let i = 0; i < this._bumps.length; i++) {
        this._addHandle(i);
    }
}

selectBump(index) {
    const handles = this._element.querySelectorAll('.bump');
    for (const handle of handles) {
        const handleIndex = parseInt(handle.dataset.index);
        if (handleIndex === index) {
            handle.classList.add('selected');
        } else {
            handle.classList.remove('selected');
        }
    }

    const color = this._bumps[index].color;
    this._binds.color.value = CommonUtils.rgb2hex([color.r, color.g, color.b]);
    this._binds.alpha.value = color.a;
}

getSelectedBumpIndex() {
    const selectedBump = this._element.querySelector('.bump.selected');
    if (selectedBump) {
        return parseInt(selectedBump.dataset.index);
    } else {
        return -1;
    }
}

getTransferFunction() {
    return this._canvas;
}

_onColorChange() {
    const selectedBump = this._element.querySelector('.bump.selected');
    const index = parseInt(selectedBump.dataset.index);
    const color = CommonUtils.hex2rgb(this._binds.color.value);
    const alpha = parseFloat(this._binds.alpha.value);
    this._bumps[index].color.r = color[0];
    this._bumps[index].color.g = color[1];
    this._bumps[index].color.b = color[2];
    this._bumps[index].color.a = alpha;
    this.render();
    this.trigger('change');
}

appendTo(object) {
    object.appendChild(this._element);
}

}
