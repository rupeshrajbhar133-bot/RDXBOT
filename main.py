import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = "8213911171:AAGXz1V8E1Ht9-1Q8YpQd8dxrQEdGScUA30"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command to show options"""
    await update.message.reply_text(
        "👋 Welcome! Kripya select karein aap kya check karna chahte hain:\n\n"
        "1️⃣ /num [number] - Phone / Details Lookup\n"
        "2️⃣ /ifsc [code] - Bank IFSC Code Details\n"
        "3️⃣ /pincode [pincode] - Postal Pincode Details\n"
        "4️⃣ /ip [ip_address] - IP Address Geolocation\n\n"
        "Example: `/num 9876543210` ya `/pincode 110001`",
        parse_mode="Markdown"
    )


# --- 1. Number Lookup Handler (Formatted Nicely) ---
async def lookup_num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Kripya number dalein.\nExample: `/num 9876543210`", parse_mode="Markdown")
        return

    query_value = args[0]
    url = f"https://free.proapis.bond/num?number={query_value}"
    
    await update.message.reply_text(f"🔍 Fetching info for `{query_value}`...", parse_mode="Markdown")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Agar data dictionary format me hai toh usey clean bullet points me convert karein
            if isinstance(data, dict) and data:
                text = f"📱 **Lookup Result for `{query_value}`:**\n\n"
                for key, value in data.items():
                    # Key ko capitalize karke clean format dena
                    formatted_key = str(key).replace('_', ' ').title()
                    text += f"• **{formatted_key}:** {value}\n"
                await update.message.reply_text(text, parse_mode="Markdown")
            else:
                # Fallback agar data list ya kuch aur ho
                await update.message.reply_text(f"✅ **Result:**\n`{data}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ API se data fetch karne me error aaya.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# --- 2. IFSC Code Handler ---
async def lookup_ifsc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Kripya IFSC code dalein.\nExample: `/ifsc HDFC0000123`", parse_mode="Markdown")
        return

    ifsc_code = args[0].upper()
    url = f"https://ifsc.razorpay.com/{ifsc_code}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            text = (
                f"🏦 **Bank Details ({ifsc_code}):**\n"
                f"• **Bank:** {data.get('BANK')}\n"
                f"• **Branch:** {data.get('BRANCH')}\n"
                f"• **City:** {data.get('CITY')}\n"
                f"• **State:** {data.get('STATE')}\n"
                f"• **Address:** {data.get('ADDRESS')}"
            )
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Invalid IFSC code or data not found.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# --- 3. Pincode Handler (Fixed & Enhanced) ---
async def lookup_pincode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Kripya Pincode dalein.\nExample: `/pincode 110001`", parse_mode="Markdown")
        return

    pincode = args[0].strip()
    url = f"https://api.postalpincode.in/pincode/{pincode}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # API response structure check karein
            if isinstance(data, list) and len(data) > 0:
                result_obj = data[0]
                status = result_obj.get('Status')
                
                if status == 'Success':
                    post_offices = result_obj.get('PostOffice', [])
                    text = f"📍 **Pincode Details ({pincode}):**\nFound {len(post_offices)} post office(s):\n\n"
                    
                    for po in post_offices[:8]:  # Max 8 post offices display karenge
                        name = po.get('Name', 'N/A')
                        district = po.get('District', 'N/A')
                        state = po.get('State', 'N/A')
                        delivery = po.get('DeliveryStatus', 'N/A')
                        text += f"🏛️ **{name}**\n   • District: {district}\n   • State: {state}\n   • Type: {delivery}\n\n"
                        
                    await update.message.reply_text(text, parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ Invalid Pincode or no records found.")
            else:
                await update.message.reply_text("❌ Invalid response format from Postal API.")
        else:
            await update.message.reply_text("❌ Failed to connect to Postal API.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# --- 4. IP Geolocation Handler ---
async def lookup_ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Kripya IP address dalein.\nExample: `/ip 8.8.8.8`", parse_mode="Markdown")
        return

    ip_address = args[0]
    url = f"https://ipwho.is/{ip_address}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                text = (
                    f"🌐 **IP Info ({data.get('ip')}):**\n"
                    f"• **Type:** {data.get('type')}\n"
                    f"• **Country:** {data.get('country')} ({data.get('country_code')})\n"
                    f"• **City:** {data.get('city')}\n"
                    f"• **Region:** {data.get('region')}\n"
                    f"• **ISP:** {data.get('connection', {}).get('isp')}"
                )
                await update.message.reply_text(text, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ API Error: {data.get('message', 'Unknown error')}")
        else:
            await update.message.reply_text("❌ Failed to fetch IP details.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Registering Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("num", lookup_num_command))
    app.add_handler(CommandHandler("ifsc", lookup_ifsc_command))
    app.add_handler(CommandHandler("pincode", lookup_pincode_command))
    app.add_handler(CommandHandler("ip", lookup_ip_command))

    print("🤖 All-in-One API Bot is running smoothly...")
    app.run_polling()


if __name__ == "__main__":
    main()
        
