import QtQuick
import "./FluentUI"

FluSlider{
    property bool needMM: true
    property int leftTextMargin: -80
    property int rightTextMargin: -60
    id: root
    tooltipEnabled: false
    enabled: false
    from: -30000
    to: 50000
    stepSize: 1

    FluText{
        id: leftText
        text: String(root.from) + (needMM ? "mm" : "")
        anchors{
            left: parent.left
            leftMargin: leftTextMargin
            verticalCenter: parent.verticalCenter
        }
        elide: Text.ElideRight
        font.pixelSize: 18
        color: "#3b4a5a"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    FluText{
        id: rightText
        text: String(root.to)  + (needMM ? "mm" : "")
        anchors{
            right: parent.right
            rightMargin: rightTextMargin
            verticalCenter: parent.verticalCenter
        }
        font.pixelSize: 18
        color: "#3b4a5a"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    FluText{
        id: topText
        text: String(root.value) + (needMM ? "mm" : "")
        anchors{
            top: parent.top
            topMargin: -20
            horizontalCenter: parent.horizontalCenter
        }
        font.pixelSize: 18
        color: "#3b4a5a"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    function setValue(data, num){
        if(num === 2){
            from = data
        }else if(num === 3){
            to = data
        }else if(num === 1){
            if (data < from) data = from
            if (data > to) data = to
            value = data
        }
    }
}
