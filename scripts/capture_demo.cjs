// Real local application tests and recording; optional Playwright tooling.
const fs=require('fs'); const path=require('path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});
  const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.APP_URL || 'http://localhost:8501',{waitUntil:'domcontentloaded'});
  await page.getByText('Tickets opened',{exact:true}).waitFor({timeout:60000});
  await page.waitForTimeout(2500);
  await page.mouse.move(0,0);
  await page.screenshot({path:'docs/img/streamlit-overview.png'});
  await page.goto(process.env.SITE_URL || 'http://localhost:8000',{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.body.dataset.ready==='All months');
  if(await page.locator('.panel').count()!==8)throw Error('Expected eight chart panels');
  if(!(await page.locator('#metrics').innerText()).includes('20,000'))throw Error('Synthetic count mismatch');
  if(process.env.SMOKE_ONLY){
    await page.selectOption('#month','2024-12-01');await page.waitForFunction(()=>document.body.dataset.ready==='2024-12-01');
    if(!(await page.locator('#metrics').innerText()).includes('1,708'))throw Error('Cohort filter mismatch');
    const download=page.waitForEvent('download');await page.click('#download');const file=await download;
    await file.saveAs('artifacts/smoke-cohort.json');
    if(JSON.parse(fs.readFileSync('artifacts/smoke-cohort.json')).opened_tickets!==1708)throw Error('Export mismatch');
    if(errors.length)throw Error(errors.join('\n'));
    console.log('Clean-clone dashboard passed: Streamlit loads, eight charts, month filter and evidence export match.');
    await browser.close();return;
  }
  fs.mkdirSync('docs/img/frames',{recursive:true});
  const start=Date.now();
  await page.mouse.move(0,0);
  for(let i=0;i<40;i++){
    if(i===7) {await page.selectOption('#month','2024-12-01');await page.waitForFunction(()=>document.body.dataset.ready==='2024-12-01');}
    if(i===14) {await page.evaluate(()=>window.scrollTo({top:650,behavior:'smooth'}));}
    if(i===22) {await page.evaluate(()=>window.scrollTo({top:1250,behavior:'smooth'}));}
    if(i===30) {await page.selectOption('#month','2024-06-01');await page.waitForFunction(()=>document.body.dataset.ready==='2024-06-01');}
    if(i===35) {
      const download=page.waitForEvent('download');await page.click('#download');
      const file=await download; await file.saveAs('artifacts/synthetic-cohort-metrics.json');
      if(JSON.parse(fs.readFileSync('artifacts/synthetic-cohort-metrics.json')).opened_tickets!==1611)throw Error('Cohort download mismatch');
    }
    await page.screenshot({path:`docs/img/frames/${String(i).padStart(3,'0')}.png`});
    const remaining=start+(i+1)*1000-Date.now();if(remaining>0)await page.waitForTimeout(remaining);
  }
  await page.mouse.move(0,0);await page.evaluate(()=>window.scrollTo(0,0));await page.waitForTimeout(400);
  await page.screenshot({path:'docs/img/dashboard-detail.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));await page.waitForTimeout(400);
  if(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+2))throw Error('Mobile overflow');
  if(errors.length)throw Error(errors.join('\n'));
  console.log('Browser checks passed: eight charts, cohort filtering, export, mobile layout, no page errors; 40-second real recording.');
  await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
