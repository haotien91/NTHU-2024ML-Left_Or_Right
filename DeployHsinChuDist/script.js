// 初始化地图
var map = L.map('map').setView([24.7455, 120.922473], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// 定义图标
var customIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// 创建聚类图层
var markerCluster = L.markerClusterGroup({
    showCoverageOnHover: false,
    spiderfyOnMaxZoom: true,
    iconCreateFunction: function(cluster) {
        return L.divIcon({ 
            html: '<div><span>' + cluster.getChildCount() + '</span></div>',
            className: 'marker-cluster marker-cluster-custom',
            iconSize: new L.Point(40, 40)
        });
    }
});

// 创建自定义的弹出窗口内容
function createPopupContent(data) {
    const images = data.images;
    let imageHtml = '';
    
    if (images.length > 0) {
        imageHtml = `
            <div class="carousel">
                <div class="carousel-container" id="carousel-${data.lat}-${data.lng}">
                    ${images.map((img, index) => `
                        <div class="carousel-slide" style="display: ${index === 0 ? 'block' : 'none'}">
                            <img src="labeled_HsinChu/${img.filename}.jpg" 
                                style="width: 100%; cursor: pointer;" 
                                onclick="window.open('labeled_HsinChu/${img.filename}.jpg', '_blank')"/>
                            <p>角度: ${img.angle}° (${index + 1}/${images.length})</p>
                        </div>
                    `).join('')}
                </div>
                ${images.length > 1 ? `
                    <button class="carousel-prev" onclick="changeSlide('${data.lat}-${data.lng}', -1)">❮</button>
                    <button class="carousel-next" onclick="changeSlide('${data.lat}-${data.lng}', 1)">❯</button>
                ` : ''}
            </div>
        `;
    }

    return `
        <div style="max-width: 300px;">
            <p>待轉區位置 (共 ${images.length} 個角度)</p>
            ${imageHtml}
            <p style="font-size: 0.8em; color: #666;">點擊圖片可以查看原始大小</p>
        </div>
    `;
}

// 幻燈片控制函数
window.currentSlides = {};
window.changeSlide = function(locationId, direction) {
    const container = document.getElementById(`carousel-${locationId}`);
    const slides = container.getElementsByClassName('carousel-slide');
    
    if (!window.currentSlides[locationId]) {
        window.currentSlides[locationId] = 0;
    }
    
    // 隐藏当前幻灯片
    slides[window.currentSlides[locationId]].style.display = 'none';
    
    // 计算新的幻灯片索引
    window.currentSlides[locationId] = (window.currentSlides[locationId] + direction + slides.length) % slides.length;
    
    // 显示新的幻灯片
    slides[window.currentSlides[locationId]].style.display = 'block';
};

// 从 JSON 文件中读取数据
fetch('leftturnbox.json')
    .then(response => response.json())
    .then(data => {
        data.forEach(function(point) {
            var marker = L.marker([point.lat, point.lng], {icon: customIcon})
                .bindPopup(createPopupContent(point));
            markerCluster.addLayer(marker);
        });

        // 添加聚类图层到地图
        map.addLayer(markerCluster);

        // 添加统计信息
        var info = L.control({position: 'bottomleft'});
        info.onAdd = function(map) {
            var div = L.DomUtil.create('div', 'legend');
            div.innerHTML = `
                <h4>待轉區統計</h4>
                <p>總位置數量: ${data.length} 個</p>
                <p>總圖片數量: ${data.reduce((sum, point) => sum + point.images.length, 0)} 張</p>
            `;
            return div;
        };
        info.addTo(map);

        // 调整地图视野
        if (data.length > 0) {
            var bounds = L.latLngBounds(data.map(point => [point.lat, point.lng]));
            map.fitBounds(bounds);
        }
    })
    .catch(error => console.error('读取数据文件时出错:', error));