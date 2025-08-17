import QtQuick
import QtQuick.Window
import "./Components"
import "./Components/FluentUI"

Window {
    id: win
    width: 576
    height: 432
    visible: true
    title: qsTr("HelloPicoWithQt")
    color: "#e9ecf3"
    property int waitTime: 0
    property bool firstRead: true

    HelloMainContainer{
        width: 520
        height: 340

        HelloSlider{
            id: topSlider
            anchors{
                horizontalCenter: parent.horizontalCenter
                top: parent.top
                topMargin: 30
            }
            width: 360
            leftTextMargin: -60
            rightTextMargin: -50
            needMM: false
        }

        HelloPositionContainer{
            id: positionSlider
            anchors{
                left: parent.left
                top: topSlider.bottom
                leftMargin: 24
                topMargin: 32
            }
        }

        HelloSpeedContainer{
            id: speedContainer
            anchors{
                right: parent.right
                top: topSlider.bottom
                rightMargin: 24
                topMargin: 32
            }
        }

        HelloFilledButton{
            anchors{
                horizontalCenter: parent.horizontalCenter
                bottom: parent.bottom
                bottomMargin: 20
            }
            width: parent.width - 40
            height: 40
            text: "Send Positon Command"
            onClicked: {
                regularReadMachineData.stop()
                win.sendDeviceCommand(4)
            }
        }
    }

    FluContentDialog{
        id: waitingPopup
        title: "Waiting Ch343 Connect..."
        contentDelegate: undefined
        buttonFlags: 0x02 | 0x04
        negativeText: "Exit"
        positiveText: "Retray"

        Timer{
            id: closeWaitingPopup
            interval: 1000
            repeat: false
            onTriggered: ()=>{
                waitingPopup.close()
            }
        }
        onNegativeClicked: ()=>{
            win.close()
        }
        onPositiveClicked: ()=>{
            win.waitDeviceConnect()
        }
    }
    FluInfoBar{
        id: winInfoBar
        root: win
    }
    Timer{
        id: deviceConnectOverTimer
        interval: 1000
        repeat: true
        onTriggered: ()=>{
            win.waitTime += 1
            if(win.waitTime > 20){
                let msg = "Over max time, machine maybe lost"
                waitingPopup.title = msg
                waitingPopup.buttonFlags = 0x02
                stop()
            }else{
                let msg = `Wait Device, ${win.waitTime}s....`
                waitingPopup.title = msg
                waitingPopup.buttonFlags = 0x00
            }
            if(!waitingPopup.visible){
                waitingPopup.open()
            }

        }
    }
    Timer{
        id: regularReadMachineData
        interval: 500
        repeat: true
        onTriggered: ()=>{
            if(win.firstRead){
                win.sendDeviceCommand(2)
                win.sendDeviceCommand(3)
                win.sendDeviceCommand(1)
                win.firstRead = false
            }else{
                win.sendDeviceCommand(1)
            }
        }
    }

    function openSerialDevice(){
        let deviceName = "USB-Enhanced-SERIAL CH343"
        let result = pyHelloSerialPort.open(deviceName, 115200)
        return result
    }
    function waitCh343Connect(){
        waitingPopup.close()
        let openResult = openSerialDevice()
        if (openResult){
            waitingPopup.title = "CH343 Open Success"
            waitingPopup.buttonFlags = 0x00
            waitingPopup.open()
            closeWaitingPopup.start()
        }else{
            waitingPopup.title = "CH343 Failed Open"
            waitingPopup.buttonFlags = 0x02 | 0x04
            waitingPopup.open()
        }
    }
    function waitDeviceConnect(){
        win.waitTime = 0
        deviceConnectOverTimer.start()
        sendDeviceCommand(0)  // R00
    }
    function onHelloSerialError(msg){
        winInfoBar.showError(msg)
    }
    function onResponseACK(command, ok){
        if(ok){
            if(command === HelloSerialConst.command_R00){
                waitingPopup.title = "Machine ACK R00"
                deviceConnectOverTimer.stop()
                closeWaitingPopup.start()
                regularReadMachineData.start()
            }else if(command === HelloSerialConst.command_W01){
                regularReadMachineData.start()
            }
        }else{
            msg = `Command: ${command} Decode Failed`
            onHelloSerialError(msg)
        }
    }
    function onResponseData(command, ok, data){
        if(ok){
            if(command === HelloSerialConst.command_R01){
                topSlider.setValue(data, 1)
                speedContainer.setValue(data, 1)
            }else if(command === HelloSerialConst.command_R02){
                topSlider.setValue(data, 2)
                positionSlider.setValue(data, 2)
            }else if(command === HelloSerialConst.command_R03){
                topSlider.setValue(data, 3)
                positionSlider.setValue(data, 3)
            }
        }else{
            let msg = `Command: ${command} Decode Failed`
            onHelloSerialError(msg)
        }
    }
    function sendDeviceCommand(num){
        if(num === 0){
            pyHelloSerialPort.qml_send_command(HelloSerialConst.command_R00)
        }else if(num === 1){
            pyHelloSerialPort.qml_send_command(HelloSerialConst.command_R01)
        }else if(num === 2){
            pyHelloSerialPort.qml_send_command(HelloSerialConst.command_R02)
        }else if(num === 3){
            pyHelloSerialPort.qml_send_command(HelloSerialConst.command_R03)
        }else{
            let value = positionSlider.positionVal.toFixed(2)
            let command = `${HelloSerialConst.command_W01} ${value}`
            pyHelloSerialPort.qml_send_command(command)
        }
    }
    Component.onCompleted: {
        pyHelloSerialPort.helloSerialError.connect(onHelloSerialError)
        pyHelloSerialPort.responseACK.connect(onResponseACK)
        pyHelloSerialPort.responseData.connect(onResponseData)
        //winInfoBar.showError("Error Test")
        waitCh343Connect()
        waitDeviceConnect()
    }
    Component.onDestruction: {
        let result = pyHelloSerialPort.close()
        console.log("串口资源释放状态", result)
    }
}
