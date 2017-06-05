var container;

var walltex = [];
var down = {'W': false, 'A': false, 'S': false, 'D': false};
var models = {};
var camera, scene, renderer, manager, stats;
var data = {};
var newData = {};
var outdata = {'username': username, 'wallnums': {}}
var mouseX = 0, mouseY = 0, loaded = false, color = 'blu';
var fov = 50;
var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;

var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.emit('getdata', outdata);
socket.emit('sendinput', {username: username, event: 'none'});

socket.on('data', function(dat) {
    //console.log("got data");
    newData = dat;
});

socket.on('connect', function() {
    console.log('connected');
});

socket.on('getname', function() {
    socket.emit('givename', {'username': username, 'gamename': gamename});
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

    camera = new THREE.PerspectiveCamera( fov, window.innerWidth / window.innerHeight, 1, 2000 );
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
    floorTexture.repeat.set(size/100, size/100);
    var floorMaterial = new THREE.MeshBasicMaterial( {map:floorTexture, side: THREE.DoubleSide} )
    var floorGeometry = new THREE.PlaneGeometry(size,size);
    var floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.position.y = -0.5
    floor.position.x = size / 2;
    floor.position.z = size / 2;
    floor.rotation.x = Math.PI / 2;
    scene.add(floor);

    // walls
    walltex = new THREE.ImageUtils.loadTexture('static/model/walltex.png');

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
    data = newData; // this way data remains constant for rendering
    requestAnimationFrame( animate );
    renderer.render(scene, camera);
    if(newData !== {})
        update();
    socket.emit('getdata', outdata);
}

function wallColor(col) {
    if(col === 'blu')
	   return 0x2609FF;
    if(col === 'org')
	   return 0xFF6709;
    if(col === 'grn')
        return 0x01DE53;
    if(col === 'red')
        return 0xEE2724;
    return 0;
}

function geomFromWall(wall) {
    var bg = new THREE.BoxGeometry(wall[1][0] - wall[0][0] + 3, 25, wall[1][1] - wall[0][1] + 3);
    ox = bg.vertices[0].x;
    oy = bg.vertices[0].y;
    oz = bg.vertices[0].z;
    for(var i = 0; i < 8; i++) {
	   bg.vertices[i].x += ox;
       bg.vertices[i].y += oy;
       bg.vertices[i].z += oz;
    }
    bg.verticesNeedUpdate = true;
    return bg;
}

function dbgWallObjs(name) {
    model = models[name];
    for(var i = 0; i < Math.min(model.walls.length, model.wallobjs.length); i++) {
        console.log(i);
        console.log(model.walls[i]);
        console.log(model.wallobjs[i].position)
        console.log(model.wallobjs[i].geometry.vertices[0]);
        console.log(model.wallobjs[i].geometry.vertices[6]);
    }
}

function update() {
    for(var name in data) {
        if(!data.hasOwnProperty(name))
            continue;
        player = data[name];
        if(player.hasOwnProperty('dead')) {
            if(models.hasOwnProperty(name)) {  // delete model and walls
                model = models[name]
                delete models[name];
                scene.remove(model);
                for(obj of model.wallobjs) {
                    scene.remove(obj);
                }
                delete model;
                if(name !== username)
                    continue;
                // spectate mode
                ratio = 1 / Math.tan(fov / 360 * Math.PI)  // A / O
                camera.position.y = ratio * (size * 11 / 10) / 2;
                camera.position.x = size / 2;
                camera.position.z = size / 2;
                console.log(camera.position);
                camera.lookAt(new THREE.Vector3(size / 2, 0, size / 2));
            }
            continue;
        }
        if(!models.hasOwnProperty(name)) { // first time
	    console.log('Loading model for ' + name);
            loadModel(name, player.color);
	    console.log('Finished loadModel call, creating model.walls');
            model = models[name];
            model.walls = player.walls;
	    model.wallobjs = [];
	    model.color = player.color;
	    model.wallmat = new THREE.MeshBasicMaterial({color: wallColor(model.color), map: walltex});
	    outdata['wallnums'][name] = model.walls.length;
            // render every wall
	    for (wall of model.walls) {
		geom = geomFromWall(wall);
		box = new THREE.Mesh(geom, model.wallmat);
		box.position.x = wall[0][0];
		box.position.y = 0;
		box.position.z = wall[0][1];
		scene.add(box);
		model.wallobjs.push(box);
	    }
        }
        else {
            model = models[name];
            if(player.hasOwnProperty('walls')) {
		if (player.updatedwall === model.walls.length - 1) {
            console.log("updating latest wall");
		    model.walls[player.updatedwall] = player.walls[0];
		    model.wallobjs[player.updatedwall].geometry = geomFromWall(player.walls[0]);
		}
		else {
            console.log("searching for correct wall to update");
		    start = model.walls[model.walls.length - 1][0];
		    var idx = 0;
		    while(idx < player.walls.length) {
			if (player.walls[idx][0] === start) {
			    model.walls[model.walls.length - 1] = player.walls[idx];
			    model.wallobjs[player.updatedwall].geometry = geomFromWall(player.walls[idx]);
			    console.log("wall found");
                break;
            }
            idx++;
		    }
		}
		var l = model.walls.length;
                model.walls = model.walls.concat(player.walls.slice(player.walls.length+model.walls.length-player.nwalls));
		for (; l < model.walls.length; l++) {
            wall = model.walls[l]
		    model.wallobjs[l] = new THREE.Mesh(geomFromWall(wall), model.wallmat);
            model.wallobjs[l].position.x = wall[0][0];
            model.wallobjs[l].position.y = 0;
            model.wallobjs[l].position.z = wall[0][1];
            scene.add(model.wallobjs[l]);
		}
		outdata['wallnums'][name] = model.walls.length;
                // render new walls
	    }
            // rerender updated wall
        }
        model = models[name]
        model.obj.position.x = player.x;
        model.obj.position.z = player.y;
        model.obj.rotation.y = 3 * Math.PI - player.dir * Math.PI / 2;
        if(name === username) {
            // Camera 1: behind 
            var cameraOffset = new THREE.Vector3(50,150,200);
            var axis = new THREE.Vector3(0,1,0);
            var angle = model.obj.rotation.y - Math.PI;
            cameraOffset.applyAxisAngle(axis,angle);

            newPos = model.obj.position.clone().add( cameraOffset );
            camera.position.x = newPos.x;
            camera.position.y = newPos.y;
            camera.position.z = newPos.z;
            //console.log("camera: ", camera.position, "\nmodel: ", model.position);
            // Camera 2: constant topdown (for dbg)
            // camera.position = model.obj.position.clone();
            //camera.position.y = 400;

            camera.lookAt( model.obj.position );
        }
    }
    stats.update();
}

init();
animate();
