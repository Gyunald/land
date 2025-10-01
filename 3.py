const bot = BotManager.getCurrentBot();

/**
 * 네이버 금융 달러 인덱스 정보를 스크래핑하여 응답합니다.
 * @param {Command} cmd 명령어 객체
 */
function scrapeDollarIndex(cmd) {
    // 함수 내부의 모든 변수는 let으로 선언합니다.
    let dollarIndexUrl = "https://finance.naver.com/marketindex/worldExchangeDetail.naver?marketindexCd=FX_USDX";
    let userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36";
    let filePath = "sdcard/bot/dollar_index.txt"; // 파일 저장 경로

    try {
        // 1. Jsoup을 사용하여 HTTP 요청 및 문서 파싱
        // .header()를 사용하여 User-Agent 설정
        let doc = org.jsoup.Jsoup.connect(dollarIndexUrl)
            .header("User-Agent", userAgent)
            .get();

        // 2. CSS 선택자를 사용하여 요소 추출
        let dollarIndexElement = doc.selectFirst("#content > div.spot > div.today > p.no_today");
        let diffElement = doc.selectFirst("#content > div.spot > div.today > p.no_exday > em:nth-child(3)");
        
        let result = "";

        if (dollarIndexElement && diffElement) {
            // 3. 텍스트 추출 및 포맷팅 (trim() 대신 text()가 공백을 자동으로 처리함)
            let dollarText = dollarIndexElement.text().trim();
            let diffText = diffElement.text().trim();

            result = `[달러 인덱스 정보]\n\n현재값: ${dollarText}\n등락폭: ${diffText}`;
            
            // 4. 결과를 파일에 저장
            FileStream.write(filePath, result);
            
            // 5. 채팅방에 응답
            cmd.reply(result);
            Log.i(`달러 인덱스 정보 스크래핑 성공: ${result}`);

        } else {
            result = "⚠️ 달러 인덱스 값을 찾을 수 없습니다. 웹사이트 구조가 변경되었을 수 있습니다.";
            cmd.reply(result);
            Log.e(result);
        }

    } catch (e) {
        // 오류 처리
        let errorMessage = "⚠️ 달러 인덱스 정보를 가져오는 중 오류가 발생했습니다.\n네트워크 상태나 웹사이트 연결을 확인해주세요.";
        cmd.reply(errorMessage);
        Log.e(`스크래핑 오류 발생: ${e.toString()}`);
    }
}

/**
 * API2 명령어 이벤트 핸들러
 * @param {Command} cmd 명령어 객체
 */
function onCommand(cmd) {
    // cmd.command는 접두사(`!`)를 제외한 명령어 이름입니다.
    if (cmd.command === "달러인덱스") {
        // 비동기 처리가 불가능하므로, 시간이 오래 걸리는 작업(Jsoup)은 봇 스크립트 스레드 내에서 직접 실행됩니다.
        // 스크래핑 로직을 실행합니다.
        scrapeDollarIndex(cmd);
    }
}

// 명령어 접두사를 '!'로 설정합니다.
bot.setCommandPrefix("!"); 

// 명령어 이벤트 리스너를 등록합니다.
bot.addListener(Event.COMMAND, onCommand);

// 참고: Jsoup 연결 및 파싱은 시간이 걸릴 수 있습니다.
// 스크래핑 도중 다른 메시지 이벤트는 여전히 처리될 수 있지만,
// 동일 스크립트 내 다른 명령어 처리는 이 작업이 끝날 때까지 대기합니다.
