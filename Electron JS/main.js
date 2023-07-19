const {app, BrowserWindow} = require('electron')

console.warn("Main process")

setTimeout(() => {
    console.warn(app.isReady())
}, 1000);

function craeteWindow() {
    const win = new BrowserWindow({
        width:800,
        height:600,
        //frame is the top bar of the window
        // frame: false,
        title: "SRP app",
        backgroundColor:"purple",
        // alwaysOnTop:true,
        webPreferences:{ 
            nodeIntegration:true
        }
    })

    // let child = new BrowserWindow({parent:win})
    // child.loadFile("child.html")

    win.loadFile("Index.html")

    //opens the dev tools on the UI
    // win.webContents.openDevTools();
}

// app.whenReady().then(craeteWindow);

// console.warn(app.isReady())

app.on('before-quit', (e)=>{
    console.log("Call before quit app")
    e.preventDefault()
})

app.on('ready', ()=>{
    craeteWindow();
    console.warn("Application is ready !")
})