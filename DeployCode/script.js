// 初始化地图
var map = L.map('map').setView([24.7455, 120.922473], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// 定义不同的图标
var answerIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

var detectedIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// 创建聚类图层
var answerCluster = L.markerClusterGroup({
    showCoverageOnHover: false,
    spiderfyOnMaxZoom: true,
    iconCreateFunction: function(cluster) {
        return L.divIcon({ 
            html: '<div><span>' + cluster.getChildCount() + '</span></div>',
            className: 'marker-cluster marker-cluster-custom-answer',
            iconSize: new L.Point(40, 40)
        });
    }
});

var detectedCluster = L.markerClusterGroup({
    showCoverageOnHover: false,
    spiderfyOnMaxZoom: true,
    iconCreateFunction: function(cluster) {
        return L.divIcon({
            html: '<div><span>' + cluster.getChildCount() + '</span></div>',
            className: 'marker-cluster marker-cluster-custom-detected',
            iconSize: new L.Point(40, 40)
        });
    }
});

// 计算匹配率的函数
function calculateMatchRate(answerList, detectedList, threshold) {
    let matches = 0;
    const totalDetected = detectedList.length;
    const totalAnswer = answerList.length;

    for (let detected of detectedList) {
        for (let answer of answerList) {
            // 计算两点之间的距离
            const distance = L.latLng([detected.lat, detected.lng])
                            .distanceTo([answer.lat, answer.lng]);
            if (distance <= threshold) {
                matches++;
                break;
            }
        }
    }

    return {
        precision: totalDetected > 0 ? (matches / totalDetected * 100).toFixed(2) : 0,
        recall: totalAnswer > 0 ? (matches / totalAnswer * 100).toFixed(2) : 0
    };
}

// 创建自定义的弹出窗口内容
function createPopupContent(data, type) {
    const imgPath = type === 'answer' ? 'LeftTurnBoxPhoto_answer/' : 'LeftTurnBoxPhoto_detected/';
    return `
        <div style="max-width: 300px;">
            <p>${type === 'answer' ? '實際待轉區位置' : '模型檢測位置'}</p>
            <p>檔案: ${data.filename}</p>
            <img src="${imgPath}${data.filename}" style="width: 100%; cursor: pointer;" 
                onclick="window.open('${imgPath}${data.filename}', '_blank')"/>
            <p style="font-size: 0.8em; color: #666;">點擊圖片可以查看原始大小</p>
        </div>
    `;
}

// 从两个 JSON 文件中读取数据
Promise.all([
    fetch('answer.json').then(response => response.json()),
    fetch('detected.json').then(response => response.json())
])
.then(([answerList, detectedList]) => {
    // 处理答案数据
    answerList.forEach(function(data) {
        var marker = L.marker([data.lat, data.lng], {icon: answerIcon})
            .bindPopup(createPopupContent(data, 'answer'));
        answerCluster.addLayer(marker);
    });

    // 处理检测数据
    detectedList.forEach(function(data) {
        var marker = L.marker([data.lat, data.lng], {icon: detectedIcon})
            .bindPopup(createPopupContent(data, 'detected'));
        detectedCluster.addLayer(marker);
    });

    // 添加聚类图层到地图
    map.addLayer(answerCluster);
    map.addLayer(detectedCluster);

    // 创建图层控制
    var overlays = {
        "實際待轉區": answerCluster,
        "模型檢測結果": detectedCluster
    };
    L.control.layers(null, overlays).addTo(map);

    // 计算并显示匹配率（设置50米为阈值）
    const matchRate = calculateMatchRate(answerList, detectedList, 50);
    
    // 添加匹配率信息到地图
    var info = L.control({position: 'bottomleft'});
    info.onAdd = function(map) {
        var div = L.DomUtil.create('div', 'legend');
        div.innerHTML = `
            <h4>檢測結果統計</h4>
            <p>準確率 (Precision): ${matchRate.precision}%</p>
            <p>召回率 (Recall): ${matchRate.recall}%</p>
            <p>實際待轉區數量: ${answerList.length}</p>
            <p>檢測到的數量: ${detectedList.length}</p>
        `;
        return div;
    };
    info.addTo(map);

    // 调整地图视野
    var allMarkers = [...answerList, ...detectedList];
    if (allMarkers.length > 0) {
        var bounds = L.latLngBounds(allMarkers.map(data => [data.lat, data.lng]));
        map.fitBounds(bounds);
    }
})
.catch(error => console.error('读取数据文件时出错:', error));