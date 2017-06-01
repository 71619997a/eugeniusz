var container;

var down = {'W': false, 'A': false, 'S': false, 'D': false};
var models = {};
var camera, scene, renderer, manager, stats;
var data = {};
var outdata = {'username': username, 'wallnums': {}}
var mouseX = 0, mouseY = 0, loaded = false, color = 'blu';

var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;

var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.emit('getdata', outdata);
socket.emit('sendinput', {username: username, event: 'none'});

socket.on('data', function(dat) {
    //console.log("got data");
    data = dat;
});

socket.on('connect', function() {
    console.log('connected');
});

socket.on('getname', function() {
    socket.emit('givename', {'username': username});
});

function sendKey(c) {
        socket.emit('sendinput', {username: username, key: c, event: 'keyboard'});
}

function keyDown(e) {
    c = String.fromCharCode(e.keyCode);
    if(c == "A" || c == "S" || c == "W" || c == "D") {
	if(down[c]) return;
	else {
	    down[c] = true;
	    return sendKey(c);
	}
    }
}

function keyUp(e) {
    c = String.fromCharCode(e.keyCode);
    if(c == "A" || c == "S" || c == "W" || c == "D")
	down[c] = false;
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


    // floor
    var floorTexture = new THREE.ImageUtils.loadTexture('static/img/checkerboard.jpg')
    floorTexture.wrapS = floorTexture.wrapT = THREE.RepeatWrapping;
    floorTexture.repeat.set(10,10);
    var floorMaterial = new THREE.MeshBasicMaterial( {map:floorTexture, side: THREE.DoubleSide} )
    var floorGeometry = new THREE.PlaneGeometry(1000,1000,10,10);
    var floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.position.y = -0.5
    floor.rotation.x = Math.PI / 2;
    scene.add(floor);

    // renderer
    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    container.appendChild( renderer.domElement );

    //stats
    stats = new Stats();
    stats.domElement.style.position = 'absolute';
    stats.domElement.style.top = '0';
    stats.domElement.style.zIndex = 100;
    container.appendChild( stats.domElement );

    // document.addEventListener( 'mousemove', onDocumentMouseMove, false );

    window.addEventListener('keydown', keyDown, false);
    window.addEventListener('keyup', keyUp, false);
    window.addEventListener( 'resize', onWindowResize, false );
    console.log(scene);
}

function loadModel(name, color, f) {
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
            models[name].obj = object;
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

function onProgress( xhr ) {
    if ( xhr.lengthComputable ) {
        var percentComplete = xhr.loaded / xhr.total * 100;
        console.log( Math.round(percentComplete, 2) + '% downloaded' );
    }
};

function onError( xhr ) {
};

function onWindowResize() {
    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );
}

// not used
function onDocumentMouseMove( event ) {
    mouseX = ( event.clientX - windowHalfX ) / 2;
    mouseY = ( event.clientY - windowHalfY ) / 2;
}

function animate() {
    requestAnimationFrame( animate );
    renderer.render(scene, camera);
    if(data !== {})
        update();
    socket.emit('getdata', outdata);
}

function update() {
    for(var name in data) {
        player = data[name];
        if(!models.hasOwnProperty(name)) { // first time
	    console.log('Loading model for ' + name);
            loadModel(name, player.color);
	    console.log('Finished loadModel call, creating model.walls');
            model = models[name];
            model.walls = player.walls;
	    outdata['wallnums'][name] = model.walls.length;
            // render every wall
        }
        else {
            model = models[name];
            model.walls[-1] = player.wallupdate
            if(player.hasOwnProperty('walls')) {
                model.walls += player.walls
		outdata['wallnums'][name] += player.walls.length;
                // render new walls
	    }
            // rerender updated wall
        }
        model = models[name]
        model.obj.position.x = player.x;
        model.obj.position.z = player.y;
        model.obj.rotation.y = 3 * Math.PI - player.dir * Math.PI / 2;
        if(name === username) {
            var cameraOffset = new THREE.Vector3(50,50,200);
            var axis = new THREE.Vector3(0,1,0);
            var angle = model.obj.rotation.y - Math.PI;
            cameraOffset.applyAxisAngle(axis,angle);

            newPos = model.obj.position.clone().add( cameraOffset );
            camera.position.x = newPos.x;
            camera.position.y = newPos.y;
            camera.position.z = newPos.z;
            //console.log("camera: ", camera.position, "\nmodel: ", model.position);
            camera.lookAt( model.obj.position );
        }
    }
    stats.update();
}

init();
animate();
