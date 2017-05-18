var WIDTH = 1980, HEIGHT = 1080;

var renderer, camera, scene;

var ball;
var speed = 1;
var dir = 0; //angle in radian

function getKey(e) {
    if (e.keyCode == 65) { // A
        dir += Math.PI/2;
    }
    if (e.keyCode == 68) { //D
        dir -= Math.PI/2;
    }
}

function setup() {
    window.addEventListener('keydown', getKey, false);

    renderer = new THREE.WebGLRenderer();
    renderer.setSize(WIDTH, HEIGHT);

    var c = document.getElementById("gameCanvas");
    c.appendChild(renderer.domElement);

    camera = new THREE.PerspectiveCamera(45,
                                         window.innerWidth/window.innerHeight,
                                         1,
                                         100);
    //camera.position.z = 50;
    scene = new THREE.Scene();
    scene.add(camera);

    //sphere
    var radius = 5, segments = 6, rings = 6;
    var sphereMaterial = new THREE.MeshLambertMaterial({color:0xD43001});
    ball = new THREE.Mesh(new THREE.SphereGeometry(radius,
                                                   segments,
                                                   rings),
                          sphereMaterial);
    scene.add(ball);

    var ambient = new THREE.AmbientLight(0x101030);
    scene.add(ambient);

    var directional = new THREE.DirectionalLight(0xffeedd);
    directional.position.set(0,0,1);
    scene.add(directional);

    //plane
    var planeMaterial = new THREE.MeshLambertMaterial({color:0x4BD121});
    var plane = new THREE.Mesh(new THREE.PlaneGeometry(1920,
                                                       1080,
                                                       10,
                                                       10),
                               planeMaterial);
    scene.add(plane);

    draw();
}

function draw() {
    var dX = Math.cos(dir);
    var dY = Math.sin(dir);
    ball.position.x += speed * dX;
    ball.position.y += speed * dY;

    // camera.position.x = ball.position.x;
    // camera.position.y = ball.position.y;
    camera.lookAt(ball.position);

    renderer.render(scene, camera);

    requestAnimationFrame(draw);
}
