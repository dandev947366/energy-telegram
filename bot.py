import logging
import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from datetime import datetime
import aiohttp
from telegram.constants import ParseMode
import httpx


# Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
NGROK_URL = os.environ.get("NGROK_URL")
API_TOKEN = os.environ.get("API_TOKEN")

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Handlers ---


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Click me!", callback_data="button_clicked")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Start here", reply_markup=reply_markup)


async def systems(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display a list of systems (without interactive buttons)"""
    url = f"{NGROK_URL}/api/systems?page=1&pageSize=10&sortOrder=asc&sortProperty=name"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }

    message = update.effective_message

    try:
        # Show loading message
        loading_msg = await message.reply_text("⏳ Fetching systems data...")

        # Make API request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        json_data = response.json()
        systems_list = json_data.get("data", {}).get("systems", [])

        if not systems_list:
            await loading_msg.edit_text("ℹ️ No systems found.")
            return

        # Build the message with system information
        msg = f"📊 *Systems List* ({len(systems_list)} found)\n\n"

        for system in systems_list[
            :10
        ]:  # Show first 10 systems to avoid message flooding
            msg += (
                f"🏢 *{system.get('name', 'Unnamed System')}*\n"
                f"🆔 ID: `{system.get('id', 'N/A')}`\n"
                f"👤 Assigned: {system.get('assign_to', 'N/A')}\n"
                f"📝 {system.get('description', 'No description')}\n\n"
            )

        if len(systems_list) > 10:
            msg += f"📋 And {len(systems_list)-10} more systems..."

        # Edit the loading message to show the final content
        await loading_msg.edit_text(text=msg, parse_mode="Markdown")

    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        await message.reply_text(
            "⚠️ Failed to connect to the server. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


async def sites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display a list of sites"""
    url = f"{NGROK_URL}/api/site?page=1&pageSize=10&sortOrder=asc&sortProperty=name&name=Office&created_by=2&assign_to=5"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }

    message = (
        update.message or update.callback_query.message or update.effective_message
    )

    try:
        await message.reply_text("⏳ Fetching site data...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        json_data = response.json()
        sites_list = json_data.get("data", {}).get("sites", [])

        if not sites_list:
            msg = "ℹ️ No sites found."
            reply_markup = None
        else:
            msg = f"✅ Found {len(sites_list)} sites:\n\n"
            keyboard = []
            for site in sites_list[:5]:
                msg += (
                    f"🏢 Name: {site.get('name', 'Unnamed')}\n"
                    f"🆔 ID: {site.get('id', 'N/A')}\n"
                    f"👤 Assigned To: {site.get('assign_to', 'N/A')}\n"
                    f"📝 Description: {site.get('description', 'No description')}\n\n"
                )
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            "Show Site", callback_data=f"show_site_{site.get('id')}"
                        )
                    ]
                )
            if len(sites_list) > 5:
                msg += f"...and {len(sites_list) - 5} more."
            reply_markup = InlineKeyboardMarkup(keyboard)
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        msg = "⚠️ Failed to connect to the server. Please try again later."
        reply_markup = None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        msg = f"❌ Error: {str(e)}"
        reply_markup = None

    await message.reply_text(msg, reply_markup=reply_markup)


async def vehicles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display a list of sites"""
    url = f"{NGROK_URL}/api/vehicle?page=1&pageSize=10&sortOrder=asc&sortProperty=name&name=Office&created_by=2&assign_to=5"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }

    message = (
        update.message or update.callback_query.message or update.effective_message
    )

    try:
        await message.reply_text("⏳ Fetching vehicles data...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        json_data = response.json()
        vehicles_list = json_data.get("data", {}).get("vehicles", [])

        if not vehicles_list:
            msg = "ℹ️ No vehicles found."
            reply_markup = None
        else:
            msg = f"✅ Found {len(vehicles_list)} vehicles:\n\n"
            keyboard = []
            for vehicle in vehicles_list[:5]:
                msg += (
                    f"🏢 Name: {vehicle.get('name', 'Unnamed')}\n"
                    f"🆔 ID: {vehicle.get('id', 'N/A')}\n"
                    f"👤 Assigned To: {vehicle.get('assign_to', 'N/A')}\n"
                    f"📝 Description: {vehicle.get('description', 'No description')}\n\n"
                )
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            "Show Vehicle",
                            callback_data=f"show_vehicle_{vehicle.get('id')}",
                        )
                    ]
                )
            if len(vehicles_list) > 5:
                msg += f"...and {len(vehicles_list) - 5} more."
            reply_markup = InlineKeyboardMarkup(keyboard)
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        msg = "⚠️ Failed to connect to the server. Please try again later."
        reply_markup = None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        msg = f"❌ Error: {str(e)}"
        reply_markup = None

    await message.reply_text(msg, reply_markup=reply_markup)


async def devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display a list of devices with only name, system, manufacturer"""
    url = f"{NGROK_URL}/api/system-device?page=1&pageSize=10&sortOrder=asc&sortProperty=name&name=Office&created_by=2&assign_to=5"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    if update.message:
        message = update.message
    elif update.callback_query:
        message = update.callback_query.message
    else:
        message = update.effective_message
    message = (
        update.message or update.callback_query.message or update.effective_message
    )

    try:
        await message.reply_text("⏳ Fetching devices data...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        json_data = response.json()
        devices_list = json_data.get("data", {}).get("systemdevices", [])

        if not devices_list:
            msg = "ℹ️ No devices found."
            reply_markup = None
        else:
            msg = f"✅ Found {len(devices_list)} devices:\n\n"
            keyboard = []
            for device in devices_list[:5]:
                external_code = device.get("external_code")

                # Skip devices without external_code
                if not external_code:
                    continue

                name = device.get("name", "Unnamed")
                attributes = device.get("attributes", {})
                info = attributes.get("information", {})
                charge = attributes.get("chargeState", {})
                system_name = (
                    device.get("systems", [{}])[0].get("name", "N/A")
                    if device.get("systems")
                    else "N/A"
                )

                msg += (
                    f"🏢 Name: {name}\n"
                    f"Battery ID: {external_code}\n"
                    f"⚙️ System: {system_name}\n"
                    f"🔋 *{name}*\n\n"
                    f"🆔 Device ID: {device.get('id')}\n"
                    f"📟 External Code: {external_code}\n"
                    f"🏭 Manufacturer: {attributes.get('vendor')} ({info.get('brand')})\n"
                    f"📺 Model: {info.get('model')}\n\n"
                    f"⚡ Battery Status:\n"
                    f"- Level: {charge.get('batteryLevel', 'N/A')}%\n"
                    f"- Capacity: {charge.get('batteryCapacity', 'N/A')} kWh\n"
                    f"- Status: {charge.get('status', 'N/A')}\n\n"
                    f"🛠 Operation Mode: {attributes.get('config', {}).get('operationMode', 'N/A')}\n"
                    f"📍 Last Seen: {attributes.get('lastSeen', 'N/A')}\n\n"
                )

                keyboard.append(
                    [
                        InlineKeyboardButton(
                            "Show Device",
                            # callback_data=f"device_control_{external_code}",
                            callback_data=f"device_control_{external_code}",
                        )
                    ]
                )

            if len(devices_list) > 5:
                msg += f"...and {len(devices_list) - 5} more."
            reply_markup = InlineKeyboardMarkup(keyboard)

    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        msg = "⚠️ Failed to connect to the server. Please try again later."
        reply_markup = None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        msg = f"❌ Error: {str(e)}"
        reply_markup = None

    await message.reply_text(msg, reply_markup=reply_markup)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_devices":
        # Call devices() to show the devices list again
        await devices(update, context)

    elif data.startswith("device_control_"):
        _, _, external_code = data.split("_", 2)
        await device_control(update, context, external_code)

    elif data.startswith("device_details_"):
        _, _, external_code = data.split("_", 2)
        await device_details_callback_router(update, context)

    else:
        await query.edit_message_text("❌ Unknown command")


async def battery_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display detailed battery status"""
    query = update.callback_query
    await query.answer()

    external_code = query.data.replace("battery_status_", "")
    url = f"{NGROK_URL}/api/batteries/{external_code}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }

    try:
        await query.edit_message_text("🔋 Fetching battery status...")

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            battery_data = response.json()

        charge_state = battery_data.get("chargeState", {})
        config = battery_data.get("config", {})
        info = battery_data.get("information", {})

        message = (
            f"🔋 *Battery Status*\n\n"
            f"🏷️ Model: {info.get('model', 'N/A')}\n"
            f"📍 Site: {info.get('siteName', 'N/A')}\n\n"
            f"⚡ Charge Level: {charge_state.get('batteryLevel', 'N/A')}%\n"
            f"🔋 Capacity: {charge_state.get('batteryCapacity', 'N/A')} kWh\n"
            f"🔌 Status: {charge_state.get('status', 'N/A')}\n"
            f"🔄 Operation Mode: {config.get('operationMode', 'N/A').replace('_', ' ')}\n"
            f"⏱️ Last Updated: {charge_state.get('lastUpdated', 'N/A')}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔄 Refresh", callback_data=f"battery_status_{external_code}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Controls",
                    callback_data=f"device_control_{external_code}",
                )
            ],
            [InlineKeyboardButton("⬅️ Back to List", callback_data="back_to_devices")],
        ]

        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.error(f"Failed to fetch battery status: {e}")
        await query.edit_message_text(
            "⚠️ Failed to fetch battery status. Please try again later."
        )


async def device_control(
    update: Update, context: ContextTypes.DEFAULT_TYPE, device_external_code: str
):
    """Show operation mode control buttons for a device"""
    if not device_external_code:
        await (update.callback_query or update).edit_message_text(
            "⚠️ This device does not support operation mode control."
        )
        return
    keyboard = [
        [
            InlineKeyboardButton(
                "⏰ Time of Use",
                callback_data=f"set_mode_{device_external_code}_TIME_OF_USE",
            ),
            InlineKeyboardButton(
                "📤 Export Focus",
                callback_data=f"set_mode_{device_external_code}_EXPORT_FOCUS",
            ),
        ],
        [
            InlineKeyboardButton(
                "📥 Import Focus",
                callback_data=f"set_mode_{device_external_code}_IMPORT_FOCUS",
            ),
            InlineKeyboardButton(
                "🔋 Self Reliance",
                callback_data=f"set_mode_{device_external_code}_SELF_RELIANCE",
            ),
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data=f"back_to_devices")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"🔧 *Operation Mode Control*\n\n"
        f"Device: `{device_external_code}`\n"
        f"Select new operation mode:"
    )

    await (update.callback_query or update).edit_message_text(
        text=message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def set_operation_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle operation mode change request"""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_", 3)
    if len(parts) != 4:
        await query.edit_message_text("❌ Invalid callback data format.")
        return

    external_code = parts[2]
    mode = parts[3]
    url = f"{NGROK_URL}/api/batteries/{external_code}/operation-mode"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"batteryId": external_code, "operationMode": mode}

    try:
        # Show loading message
        await query.edit_message_text(f"🔄 Setting {mode.replace('_', ' ')} mode...")

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()

        # Show success message
        message = (
            f"✅ Successfully set operation mode to *{mode.replace('_', ' ')}*\n\n"
            f"Device: `{external_code}`\n"
            f"New Mode: {mode}"
        )

        # Add refresh and back buttons
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔄 Get Battery Status",
                    callback_data=f"battery_status_{external_code}",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Controls",
                    callback_data=f"device_control_{external_code}",
                )
            ],
            [InlineKeyboardButton("⬅️ Back to List", callback_data="back_to_devices")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )

    except httpx.RequestError as e:
        logger.error(f"API request failed: {e}")
        await query.edit_message_text(
            "⚠️ Failed to update operation mode. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await query.edit_message_text(f"❌ Error: {str(e)}")


countries = {
    "Greece": "10YGR-HTSO-----Y",
    "Germany": "10Y1001A1001A82H",
    "France": "10YFR-RTE------C",
    "Spain": "10YES-REE------0",
    "Italy": "10Y1001A1001A44P",
}


async def marketprices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show country selection for market prices"""
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"prices_{code}")]
        for name, code in countries.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await (update.message or update.effective_message).reply_text(
        "🌍 Select a country for market prices:", reply_markup=reply_markup
    )


async def show_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show prices for selected country"""
    query = update.callback_query
    await query.answer()

    country_code = query.data.replace("prices_", "")
    url = f"{NGROK_URL}/api/market-price/day-ahead?country={country_code}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }

    await query.edit_message_text("⏳ Fetching market prices...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                json_response = await response.json()

        price_data = json_response.get("data", [])

        if not price_data:
            msg = "ℹ️ No price data available for this country."
        else:
            country_name = next(
                (name for name, code in countries.items() if code == country_code),
                country_code,
            )

            msg = f"📊 Market Prices for {country_name}:\n\n"

            # Group by date
            prices_by_date = {}
            for entry in price_data:
                dt = datetime.fromisoformat(entry["time"].replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
                prices_by_date.setdefault(date_str, []).append(entry)

            # Sort dates to show consistently
            for i, (date, prices) in enumerate(sorted(prices_by_date.items())):
                if i >= 2:
                    break

                msg += f"📅 {date}\n"
                for entry in prices[:24]:
                    dt = datetime.fromisoformat(entry["time"].replace("Z", "+00:00"))
                    price = entry.get("price")
                    msg += f"• {dt.strftime('%H:%M')} - {price} €/MWh\n"
                msg += "\n"

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔄 Refresh", callback_data=f"prices_{country_code}"
                )
            ],
            [InlineKeyboardButton("🌍 Change Country", callback_data="change_country")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=msg, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        await query.edit_message_text(
            "⚠️ Failed to fetch prices. Please try again later."
        )


async def change_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle change country request"""
    query = update.callback_query
    await query.answer()
    await marketprices(update, context)


async def back_to_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await devices(update, context)


async def device_control_callback_router(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    # Extract external code
    try:
        _, _, external_code = query.data.split("_", 2)
        await device_control(update, context, external_code)
    except Exception as e:
        logger.error(f"device_control router failed: {e}")
        await query.edit_message_text("❌ Failed to load operation mode controls.")


async def device_details_callback_router(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    try:
        print("Callback data:", query.data)  # Debug print

        if query.data == "back_to_devices":
            # Call your devices function to show list again
            await devices(update, context)
            return

        # Otherwise, expect callback like device_details_{external_code}
        _, _, external_code = query.data.split("_", 2)
        await device_control(update, context, external_code)

    except Exception as e:
        logger.error(f"device_details router failed with data '{query.data}': {e}")
        await query.edit_message_text("❌ Failed to go back to device controls.")


# --- Main Execution ---
def main():
    logger.info("Starting bot...")
    if not TELEGRAM_TOKEN:
        raise ValueError("Missing TELEGRAM_TOKEN environment variable")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("devices", devices))
    app.add_handler(CommandHandler("sites", sites))
    app.add_handler(CommandHandler("systems", systems))
    app.add_handler(CommandHandler("vehicles", vehicles))
    app.add_handler(CommandHandler("marketprices", marketprices))
    app.add_handler(CallbackQueryHandler(show_prices, pattern="^prices_"))
    app.add_handler(CallbackQueryHandler(back_to_devices, pattern="^back_to_devices$"))
    app.add_handler(CallbackQueryHandler(change_country, pattern="^change_country$"))
    app.add_handler(
        CallbackQueryHandler(device_control_callback_router, pattern="^device_control_")
    )
    app.add_handler(CallbackQueryHandler(set_operation_mode, pattern="^set_mode_"))
    app.add_handler(
        CallbackQueryHandler(
            device_details_callback_router, pattern=r"^device_details_"
        )
    )
    app.add_handler(CallbackQueryHandler(battery_status, pattern="^battery_status_"))
    app.run_polling()


if __name__ == "__main__":
    main()
