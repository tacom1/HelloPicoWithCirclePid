import QtQuick
import "./FluentUI"
import pyTools

Rectangle {
    width: parent.width / 2 - 30
    height: 160
    color: "#00000000"
    border.color: "white"
    border.width: 2
    radius: 10

    FluShadow{
        radius: 10
    }

    FluText{
        id: speedText
        text: "Speed"
        color: "#303e51"
        font.bold: true
        //font.weight: Font.Medium
        font.pixelSize: 20

        anchors{
            top: parent.top
            left: parent.left
            leftMargin: 5
            topMargin: 5
        }
    }

    FluText{
        id: trueText
        text: "0.00 mm/s"
        anchors{
            centerIn: parent
        }
        font.pixelSize: 32
        color: "#3b4a5a"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    HelloSpeedScripts{
        id: pyHelloSpeed
    }

    Timer{
        id: regularSpeedCalcTimer
        interval: 600
        repeat: true
        onTriggered: ()=>{
            let speed = pyHelloSpeed.getSpeed()
            //console.log(speed)
            let msg = `${speed} mm/s`
            trueText.text = msg
        }
    }

    function setValue(data, num){
        if(num === 1){
            pyHelloSpeed.appendRecord(data)
        }
    }

    Component.onCompleted: {
        regularSpeedCalcTimer.start()
    }

}
