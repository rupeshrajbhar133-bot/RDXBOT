import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# States for Menu / Input selection
CHOOSING, GET_DATA = range(2)

BOT_TOKEN = "8213911171:AAH2JDDmtWeDkVH3DBZUOgOt_FZrPzeA-EY"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command to show options"""
    await update.message.reply_text(
        "👋 Welcome! Kripya select karein aap kya check karna chahte hain:\n\n"
        "1️⃣ /num - Phone Number / Aadhaar Lookup\n"
        "2️⃣ /ifsc - Bank IFSC Code Details\n"
        "3️⃣ /pincode - Postal Pincode Details\n"
        "4️⃣ /ip - IP Address Geolocation\n\n"
        "Ya seedhe command type karein (jaise `/num 9876543210` ya `/ifsc HDFC0000123`)."
    )
    return CHOOSING


async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    return CHOOSING


# --- 1. Number / Aadhaar Lookup Handler ---
async def lookup_num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Kripya number dalein. Example: `/num 9876543210`", parse_mode="Markdown")
        return

    query_value = args[0]
    url = f"https://free.proapis.bond/num?number={query_value}"
    
    await update.message.reply_text(f"🔍 Fetching info for `{query_value}`...", parse_mode="Markdown")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            await update.message.reply_text(f"✅ **Result:**\n```json\n{data}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ API se data fetch karne me error aaya.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# --- 2. IFSC Code Handler ---
async def lookup_ifsc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Kripya IFSC code dalein. Example: `/ifsc HDFC0000123`", parse_mode="Markdown")
        return

    ifsc_code = args[0].upper()
    url = f"https://ifsc.razorpay.com/{ifsc_code}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            text = (
                f"🏦 **Bank Details:**\n"
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


# --- 3. Pincode Handler ---
async def lookup_pincode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Kripya Pincode dalein. Example: `/pincode 110001`", parse_mode="Markdown")
        return

    pincode = args[0]
    url = f"https://api.postalpincode.in/pincode/{pincode}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and data[0].get('Status') == 'Success':
                post_offices = data[0].get('PostOffice', [])
                text = f"📍 **Pincode Details ({pincode}):**\nFound {len(post_offices)} post office(s):\n"
                for po in post_offices[:5]: # Max 5 display karenge taaki message lamba na ho
                    text += f"• {po.get('Name')} ({po.get('District')}, {po.get('State')})\n"
                await update.message.reply_text(text, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Invalid Pincode or no records found.")
        else:
            await update.message.reply_text("❌ Failed to fetch pincode details.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# --- 4. IP Geolocation Handler ---
async def lookup_ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Kripya IP address dalein. Example: `/ip 8.8.8.8`", parse_mode="Markdown")
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
                await update.message.reply_text(f"❌ API Error: {data.get('message')}")
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

    print("🤖 All-in-One API Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
    
