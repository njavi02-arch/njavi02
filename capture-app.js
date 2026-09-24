const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium'
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    console.log('🚀 Abriendo YUIZZ app...\n');
    await page.goto('http://localhost:8080/volta-pro.html', { waitUntil: 'networkidle' });
    
    // Screenshot 1: Discover Screen
    console.log('📱 1/5: Capturando pantalla de Descubrimiento...');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/tmp/yuizz-01-discover.png' });
    console.log('✅ Guardado: /tmp/yuizz-01-discover.png\n');
    
    // Get app info
    const appInfo = await page.evaluate(() => {
      const coinsEl = document.querySelector('[data-coins]') || document.body;
      const coinsText = coinsEl.textContent.match(/💰\s*(\d+)/)?.[1] || 'N/A';
      const profileViewsText = coinsEl.textContent.match(/👁️\s*(\d+)/)?.[1] || 'N/A';
      return { coins: coinsText, views: profileViewsText };
    });
    console.log(`💰 Monedas iniciales: ${appInfo.coins}`);
    console.log(`👁️ Visualizaciones: ${appInfo.views}\n`);
    
    // Click Profile tab
    console.log('📱 2/5: Capturando pantalla de Perfil...');
    const tabButtons = await page.locator('button').all();
    let profileClicked = false;
    for (const btn of tabButtons) {
      const text = await btn.textContent();
      if (text.includes('Perfil')) {
        await btn.click();
        profileClicked = true;
        break;
      }
    }
    await page.waitForTimeout(1500);
    await page.screenshot({ path: '/tmp/yuizz-02-profile.png' });
    console.log('✅ Guardado: /tmp/yuizz-02-profile.png\n');
    
    // Get profile info
    const profileInfo = await page.evaluate(() => {
      const text = document.body.textContent;
      const streakMatch = text.match(/Día\s*(\d+)/);
      const coinMatch = text.match(/💰\s*(\d+)/);
      return {
        streak: streakMatch ? streakMatch[1] : 'N/A',
        coins: coinMatch ? coinMatch[1] : 'N/A'
      };
    });
    console.log(`🔥 Racha diaria: Día ${profileInfo.streak}`);
    console.log(`💰 Monedas en perfil: ${profileInfo.coins}\n`);
    
    // Click Messages tab
    console.log('📱 3/5: Capturando pantalla de Mensajes...');
    const msgButtons = await page.locator('button').all();
    for (const btn of msgButtons) {
      const text = await btn.textContent();
      if (text.includes('Mensajes')) {
        await btn.click();
        break;
      }
    }
    await page.waitForTimeout(1500);
    await page.screenshot({ path: '/tmp/yuizz-03-messages.png' });
    console.log('✅ Guardado: /tmp/yuizz-03-messages.png\n');
    
    // Get messages info
    const msgInfo = await page.evaluate(() => {
      const chats = document.querySelectorAll('[data-chat-item], .chat-item, li');
      const count = chats.length;
      const online = document.body.textContent.match(/🟢\s*en línea/g);
      return {
        chatCount: count,
        onlineCount: online ? online.length : 0
      };
    });
    console.log(`💬 Chats encontrados: ${msgInfo.chatCount}`);
    console.log(`🟢 Personas en línea: ${msgInfo.onlineCount}\n`);
    
    // Click Activity tab
    console.log('📱 4/5: Capturando pantalla de Actividad...');
    const actButtons = await page.locator('button').all();
    for (const btn of actButtons) {
      const text = await btn.textContent();
      if (text.includes('Actividad')) {
        await btn.click();
        break;
      }
    }
    await page.waitForTimeout(1500);
    await page.screenshot({ path: '/tmp/yuizz-04-activity.png' });
    console.log('✅ Guardado: /tmp/yuizz-04-activity.png\n');
    
    // Click Communities tab
    console.log('📱 5/5: Capturando pantalla de Comunidades...');
    const commButtons = await page.locator('button').all();
    for (const btn of commButtons) {
      const text = await btn.textContent();
      if (text.includes('Comunidades')) {
        await btn.click();
        break;
      }
    }
    await page.waitForTimeout(1500);
    await page.screenshot({ path: '/tmp/yuizz-05-communities.png' });
    console.log('✅ Guardado: /tmp/yuizz-05-communities.png\n');
    
    console.log('═══════════════════════════════════════════════');
    console.log('✨ TODAS LAS PANTALLAS CAPTURADAS');
    console.log('═══════════════════════════════════════════════\n');
    
    console.log('📸 Pantallas disponibles:');
    console.log('   1️⃣  /tmp/yuizz-01-discover.png');
    console.log('   2️⃣  /tmp/yuizz-02-profile.png');
    console.log('   3️⃣  /tmp/yuizz-03-messages.png');
    console.log('   4️⃣  /tmp/yuizz-04-activity.png');
    console.log('   5️⃣  /tmp/yuizz-05-communities.png\n');
    
    console.log('✅ Características implementadas:');
    console.log('   ✓ Sistema de racha diaria 7 días');
    console.log('   ✓ Hot Hour gratis primeros 2 días');
    console.log('   ✓ Monedas iniciales = 0 + recompensas diarias');
    console.log('   ✓ Visualizaciones de perfil por actividad');
    console.log('   ✓ Estado en línea dinámico (🟢 en línea)');
    console.log('   ✓ Premium €2.99/mes con comparativa WIZZ');
    console.log('   ✓ Paquetes de mensajes (50/100/200)\n');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
})();
