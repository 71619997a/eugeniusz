// taken from three.js demo

var container;

var models = {};
var camera, scene, renderer, manager;
var data = {};
var mouseX = 0, mouseY = 0, loaded = false, color = 'blu';

var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;

var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.emit('getdata', {'username': username});
socket.emit('sendinput', {username: username, event: 'none'});

socket.on('data', function(dat) {
    console.log("got data");
    data = dat;
});

socket.on('connect', function() {
    console.log('connected');
});

socket.on('getname', function() {
    socket.emit('givename', {'username': username});
});

function key(e, t) {
    console.log('key event');
    c = String.fromCharCode(e.keyCode);
    if(c == "A" || c == "S" || c == "W" || c == "D") {
        socket.emit('sendinput', {username: username, key: c, event: 'keyboard', type: t});
    }
}

function keyDown(e) {
    return key(e, 'down');
}

function keyUp(e) {
    return key(e, 'up');
}

function init() {

    container = document.createElement( 'div' );
    document.body.appendChild( container );

    camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 2000 );
    camera.position.z = 250;

    // scene

    scene = new THREE.Scene();

    var ambient = new THREE.AmbientLight( 0x606060 );
    scene.add( ambient );

    var directionalLight = new THREE.DirectionalLight( 0xffeedd );
    directionalLight.position.set( 0, 0, 1 );
    scene.add( directionalLight );

    // texture

    manager = new THREE.LoadingManager();
    manager.onProgress = function ( item, loaded, total ) {

        console.log( item, loaded, total );

    };

    var texture = new THREE.Texture();


    // var loader = new THREE.ImageLoader( manager );
    // loader.load( 'static/model/SLC_mat1_d.tga', function ( image ) {

    // 	texture.image = image;
    // 	texture.needsUpdate = true;

    // } );

    // model
    //loadModel(username, 'blu');
    //

    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    container.appendChild( renderer.domElement );

    document.addEventListener( 'mousemove', onDocumentMouseMove, false );
    // document.addEventListener('click', onDocumentClick, false);
    //
    window.addEventListener('keydown', keyDown, false);
    window.addEventListener('keyup', keyUp, false);
    window.addEventListener( 'resize', onWindowResize, false );
    console.log(scene);
}

var loadModel = function(name, color, f) {
    i = models.length;
    models[name] = {}
    models[name].loaded = false;
    var mtlloader = new THREE.MTLLoader(manager);
    mtlloader.setPath('static/model/');
    mtlloader.load('SLC_' + color + '.mtl', function(materials) {
        materials.preload();
        var objloader = new THREE.OBJLoader( manager );
        objloader.setMaterials(materials);
        objloader.setPath('static/model/');
        objloader.load( 'SLC.obj', function ( object ) {
            models[name] = object;
            models[name].loaded = true;
            // object.traverse( function ( child ) {

            // 	if ( child instanceof THREE.Mesh ) {

            // 		child.material.map = texture;

            // 	}

            // } );
            // console.log(object.position);
            // console.log(object.scale);
            // console.log(object.quaternion);
            object.scale.x = 15;
            object.scale.y = 15;
            object.scale.z = 15;
            //object.position.y = -95;
            scene.add( object );
            if(f) f();
        }, onProgress, onError );
    }, onProgress, onError);
};

var onDocumentClick = function( e ) {
    if(color == 'blu')
        color = 'red';
    else
        color = 'blu';
    oldModel = model;
    loadModel(color, function() {
        scene.remove(oldModel);
    });
}

var onProgress = function ( xhr ) {
    if ( xhr.lengthComputable ) {
        var percentComplete = xhr.loaded / xhr.total * 100;
        console.log( Math.round(percentComplete, 2) + '% downloaded' );
    }
};

var onError = function ( xhr ) {
};

function onWindowResize() {

    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

function onDocumentMouseMove( event ) {

    mouseX = ( event.clientX - windowHalfX ) / 2;
    mouseY = ( event.clientY - windowHalfY ) / 2;

}

//

function animate() {

    requestAnimationFrame( animate );
    console.log(data);
    if(data !== {})
        render();
    socket.emit('getdata', {'username': username});
}

function render() {

    //camera.position.x += ( mouseX - camera.position.x ) * .05;
    //camera.position.y += ( - mouseY - camera.position.y ) * .05;

    //camera.lookAt( scene.position );
    for(var name in data) {
        player = data[name];
        if(!models.hasOwnProperty(name))
            loadModel(name, 'red');
        model = models[name]
        model.position.x = player.pos[0];
        model.position.z = player.pos[1];
	model.rotation.y = player.dir * Math.PI / 2;

    }
    scene.rotation.y = mouseX / window.innerWidth * 4 * Math.PI + Math.PI / 2;
    scene.rotation.x = mouseY / window.innerHeight * 4 * Math.PI;
    renderer.render( scene, camera );

}


init();
animate();
