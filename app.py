import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/ip-info/<ip_address>', methods=['GET'])
def get_ip_info(ip_address):
    url = f"https://checkip.com.vn/locator?host={ip_address}"
    
    try:
        # Gửi request đến trang web
        response = requests.get(url)
        response.raise_for_status()
        
        # Phân tích HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trích xuất thông tin chi tiết
        info_table = soup.select_one('div.mt-4 table')
        rows = info_table.find_all('tr')
        
        # Xử lý dữ liệu từ bảng
        ip_info = {}
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                key = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                ip_info[key] = value
        
        # Trích xuất thông tin bổ sung
        ip_span = soup.select_one('.bg-e9 span.text-c00')
        if ip_span:
            ip_info['Your IP'] = ip_span.get_text(strip=True)
            # Tìm thẻ span kế tiếp cho location
            location_span = ip_span.find_next_sibling('span')
            if location_span:
                ip_info['Location'] = location_span.get_text(strip=True)
        
        # Chuẩn hóa tên key
        mapping = {
            'Địa chỉ IP': 'ip_address',
            'Tên máy chủ': 'hostname',
            'Nhà cung cấp': 'isp',
            'Đơn vị': 'organization',
            'Quốc gia': 'country',
            'Khu vực': 'region',
            'Múi giờ': 'timezone',
            'Giờ địa phương': 'local_time',
            'Châu lục': 'continent'
        }
        
        standardized_info = {}
        for key, value in ip_info.items():
            if key in mapping:
                standardized_info[mapping[key]] = value
        
        return jsonify(standardized_info)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
