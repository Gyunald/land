const bot = BotManager.getCurrentBot();

// --- 유틸리티 함수: 지수 상태에 따른 부호 반환 ---
/**
 * 지수 등락 텍스트에 따라 부호(이모지)를 결정합니다.
 * @param {string} compareText 등락 상태 텍스트 ("상승", "하락", "보합")
 * @returns {string} 해당 부호 (▲, ▼, ━)
 */
function getSign(compareText) {
    let sign = "━"; // 기본값: 보합
    if (compareText === "상승") {
        sign = "▲";
    } else if (compareText === "하락") {
        sign = "▼";
    }
    return sign;
}

// --- 헬퍼 함수 1: 국내 주요 지수 조회 (기존 URL1) ---
function getStockIndices() {
    let resultText = "";
    
    try {
        let URL = 'https://m.stock.naver.com/front-api/domestic/index/majors';
        let connection = org.jsoup.Jsoup.connect(URL).ignoreContentType(true);
        let jsonString = connection.execute().body();
        let data = JSON.parse(jsonString);
        
        if (!data.isSuccess || !data.result || data.result.length === 0) {
            return "❌ 국내 지수 정보를 가져오는 데 실패했습니다. (API 응답 오류)";
        }

        resultText = "📈 **대한민국 주요 지수 현황**\n" + "=".repeat(25) + "\n";
        
        for (let item of data.result) {
            let stockName = item.stockName;
            let closePrice = item.closePrice;
            let fluctuationsRatio = item.fluctuationsRatio;
            let compareText = item.compareToPreviousPrice.text;
            let sign = getSign(compareText);
            
            resultText += `${stockName}: ${closePrice} (${sign} ${fluctuationsRatio}%)\n`;
        }
        
    } catch (e) {
        Log.e("getStockIndices() 오류: " + e.message);
        return "❌ 국내 지수 정보를 가져오거나 처리하는 중 오류가 발생했습니다. (자세한 내용은 로그 확인)";
    }

    // 긴 메시지 처리 방식 추가 (보기 좋게)
    let VIEW_MORE = "\u200b".repeat(500); 
    return resultText + VIEW_MORE + "\n(데이터는 네이버 금융 기준)";
}

// --- 헬퍼 함수 2: 해외 주요 지수 조회 (추가 URL2) ---
function getWorldStockIndices() {
    let resultText = "";
    
    try {
        let URL = 'https://polling.finance.naver.com/api/realtime/worldstock/index/.DJI%2C.IXIC%2C.DJT%2C.NDX%2C.INX%2C.SOX%2C.VIX';
        let connection = org.jsoup.Jsoup.connect(URL).ignoreContentType(true);
        let jsonString = connection.execute().body();
        let data = JSON.parse(jsonString);
        
        if (!data.datas || data.datas.length === 0) {
            return "❌ 해외 지수 정보를 가져오는 데 실패했습니다. (API 응답 오류)";
        }

        resultText = "🇺🇸 **미국 주요 지수 현황**\n" + "=".repeat(25) + "\n";
        
        for (let item of data.datas) {
            let indexName = item.indexName;
            let closePrice = item.closePrice;
            let fluctuationsRatio = item.fluctuationsRatio;
            let compareText = item.compareToPreviousPrice.text;
            let sign = getSign(compareText);
            
            // 등락폭을 절대값이 아닌 실제값(compareToPreviousClosePrice)으로 표시
            let comparePrice = item.compareToPreviousClosePrice;
            
            resultText += `${indexName}: ${closePrice} (${sign} ${comparePrice} | ${fluctuationsRatio}%)\n`;
        }
        
    } catch (e) {
        Log.e("getWorldStockIndices() 오류: " + e.message);
        return "❌ 해외 지수 정보를 가져오거나 처리하는 중 오류가 발생했습니다. (자세한 내용은 로그 확인)";
    }

    let VIEW_MORE = "\u200b".repeat(500); 
    return resultText + VIEW_MORE + "\n(데이터는 네이버 금융 기준)";
}


/**
 * API2 Command event handler: 명령어를 처리합니다.
 * @param {Command} cmd Command object
 */
function onCommand(cmd) {
    // 함수 내 변수는 모두 let으로 선언해야 합니다.
    let responseMessage = "";

    try {
        if (cmd.command === "주요지수") {
            responseMessage = getStockIndices();
        } else if (cmd.command === "해외지수") {
            responseMessage = getWorldStockIndices();
        }

        if (responseMessage) {
            cmd.reply(responseMessage);
        }
    } catch (e) {
        Log.e("onCommand 처리 중 오류: " + e.message);
        cmd.reply("명령어 처리 중 내부 오류가 발생했습니다.");
    }
}

// 봇 설정 및 이벤트 리스너 등록
bot.setCommandPrefix("!"); // 명령어 접두사를 '!'로 설정
bot.addListener(Event.COMMAND, onCommand);
