// taken from three.js demo
socket.emit('getdata', {'username': username});
var container;

var camera, scene, renderer, model, manager;
var data = {}
var mouseX = 0, mouseY = 0, loaded = false, color = 'blu';

var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('data', function(dat) {
    console.log("received data");
    data = dat;
})

function init() {

    container = document.createElement( 'div' );
    document.body.appendChild( container );

    camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 2000 );
    camera.position.z = 250;

    // scene

    scene = new THREE.Scene();

    var ambient = new THREE.AmbientLight( 0x101030 );
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
    loadModel('blu');
    //

    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    container.appendChild( renderer.domElement );

    document.addEventListener( 'mousemove', onDocumentMouseMove, false );
    document.addEventListener('click', onDocumentClick, false);
    //

    window.addEventListener( 'resize', onWindowResize, false );
    console.log(scene);
}

var loadModel = function(color, f) {
    var mtlloader = new THREE.MTLLoader(manager);
    mtlloader.setPath('static/model/');
    mtlloader.load('SLC_' + color + '.mtl', function(materials) {
        materials.preload();
        var objloader = new THREE.OBJLoader( manager );
        objloader.setMaterials(materials);
        objloader.setPath('static/model/');
        objloader.load( 'SLC.obj', function ( object ) {
            model = object;
            loaded = true;
            // object.traverse( function ( child ) {

            // 	if ( child instanceof THREE.Mesh ) {

            // 		child.material.map = texture;

            // 	}

            // } );
            // console.log(object.position);
            // console.log(object.scale);
            // console.log(object.quaternion);
            object.scale.x = 30;
            object.scale.y = 30;
            object.scale.z = 30;
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
    if(loaded) {
	console.log(data);
        render();
	socket.emit('getdata', {'username': username});
	
    }
    else
        console.log('Loading...');

}

function render() {

    //camera.position.x += ( mouseX - camera.position.x ) * .05;
    //camera.position.y += ( - mouseY - camera.position.y ) * .05;

    //camera.lookAt( scene.position );
    model.position.x = data.pos[0];
    model.rotation.y = mouseX / window.innerWidth * 4 * Math.PI + Math.PI / 2;
    model.rotation.x = mouseY / window.innerHeight * 4 * Math.PI;
    renderer.render( scene, camera );

}


init();
animate();
