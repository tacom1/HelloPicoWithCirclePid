import QtQuick
import "./FluentUI"

Rectangle {
    width: parent.width / 2 - 30
    height: 160
    color: "#00000000"
    border.color: "white"
    border.width: 2
    radius: 10

    property int leftEncode: 0
    property int rightEncode: 0
    property real positionVal: 0.00

    FluShadow{
        radius: 10
    }

    HelloSliderForPositionContainer{
        id: slider
        width: parent.width - 20
        anchors{
            top: positionText.bottom
            topMargin: 80
            horizontalCenter: parent.horizontalCenter
        }

        from: 0.00
        to: 20.01
        stepSize: 0.01
        value: 0.00
        leftTextMargin: -50
        rightTextMargin: -75
        onValueChanged: {
            positionVal = value
        }
    }

    FluText{
        id: positionText
        text: "Position"
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

    function calcDistance(){
        if(rightEncode !== 0 && leftEncode !== 0){
            let encodeAll = rightEncode - leftEncode
            let toValue = (encodeAll / 2400 * 0.8).toFixed(2) // mm
            slider.to = toValue
        }
    }
    function setValue(data, num){
        if(num === 2){
            leftEncode = data
        }else if(num === 3){
            rightEncode = data
        }
        calcDistance()
    }
}
