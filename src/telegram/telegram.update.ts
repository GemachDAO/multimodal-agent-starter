import {
    Update,
    Ctx,
    Start,
    Help,
    On,
} from 'nestjs-telegraf';
import { Context } from 'telegraf';
import axios from 'axios'
import { ConfigService } from '@nestjs/config';
@Update()
export class TelegramUpdate {
    private aiAgentURL: string
    private daoGroupId: number
    constructor(private readonly configService: ConfigService) {
        this.aiAgentURL = configService.get('AI_AGENT_URL')
        this.daoGroupId = -1001531445636
    }
    @Start()
    async start(@Ctx() ctx: Context) {
        const userId = this.extractUserId(ctx)
        const isMessageFromGroup = this.isMessageFromGroup(ctx)
        if (!isMessageFromGroup) {
            const isMember = await this.isUserInGroup(this.daoGroupId, userId)
            if (isMember) {
                await this.sendAIAgentResponse(ctx)
            } else {
                await ctx.reply(`
                🚀 Greetings, space traveler! 🌌

    To fully embark on this DeFi journey with Gemach Alpha Intelligence aboard the Starship Gemach, you'll need to be part of our esteemed DAO community. Here's how:

    1. Secure a minimum of \`${this.numberWithCommas(this.configService.get('GMAC_REQUIRED_FOR_ACCESS'))} GMAC\`  tokens.
    2. Join our community by [clicking here](https://telegram.me/collablandbot?start=VFBDI1RFTCNDT01NIy0xMDAxNTMxNDQ1NjM2).
    3. Once you're in, return to this AI bot and type \`/start\` to unlock 
    a universe of DeFi insights and strategies.

    We're excited to have you onboard! 🚀
                `, { parse_mode: 'Markdown' })
            }
        }
    }

    @Help()
    async help(@Ctx() ctx: Context) {
        await ctx.reply(`
        🚀 *Starship Gemach Help Guide* 🌌\n*Start*: Kick off your DeFi journey with Gemach Alpha Intelligence.\n\n*Security Checks*:\n\n- *Phishing*: Verify if a URL is a phishing site.\n- *Address Info*: Get security details for an address.\n- *NFT Info*: Fetch NFT security details.\n- *dApp Risk*: Assess dApp risk via its URL.\n- *Token Approvals*: Check ERC-20 token approvals.\n- *ABI Decode*: Decode ABI information.\n- *Token Info*: Retrieve token security details.\n\n*Market Insights*:\n\n-*Top Coins*: Fetch the current top-performing coins.\n\nFor a smooth journey, ensure you provide all necessary details in your requests. Dive deep, strategize, and let's conquer the DeFi universe together!
        `, {
            parse_mode: 'Markdown'
        });
    }
    @On('text')
    async handleTextResponse(@Ctx() ctx: Context) {
        const userId = this.extractUserId(ctx)
        let canProcessMessage: boolean
        const isMessageSentToBot = this.isMessageSentToBot(ctx)
        const isMessageFromGroup = this.isMessageFromGroup(ctx)
        const isDAOMember = await this.isUserInGroup(this.daoGroupId, userId)

        if (isMessageFromGroup) {
            canProcessMessage = isDAOMember && isMessageSentToBot
            if (canProcessMessage) {
                await this.sendAIAgentResponse(ctx)
            }
        } else {
            if (isDAOMember) {
                await this.sendAIAgentResponse(ctx)
            } else {
                await ctx.reply(`
                🚀 Greetings, space traveler! 🌌

    To fully embark on this DeFi journey with Gemach Alpha Intelligence aboard the Starship Gemach, you'll need to be part of our esteemed DAO community. Here's how:

    1. Secure a minimum of \`${this.numberWithCommas(this.configService.get('GMAC_REQUIRED_FOR_ACCESS'))} GMAC\`  tokens.
    2. Join our community by [clicking here](https://telegram.me/collablandbot?start=VFBDI1RFTCNDT01NIy0xMDAxNTMxNDQ1NjM2).
    3. Once you're in, return to this AI bot and type \`/start\` to unlock 
    a universe of DeFi insights and strategies.

    We're excited to have you onboard! 🚀
                `, { parse_mode: 'Markdown' })
            }
        }

    }
    private isMessageFromGroup(ctx: Context): boolean {
        const isFromGroup = 'message' in ctx.update && (ctx.update.message.chat.type == "group" || ctx.update.message.chat.type == "supergroup") ? true : false
        return isFromGroup
    }
    private isMessageSentToBot(ctx: Context): boolean {
        const prefix = `@${ctx.botInfo.username}`;
        const messageText = this.extractText(ctx);

        if (messageText && messageText.startsWith(prefix)) {
            return true;
        }
        return false;
    }

    private numberWithCommas(x: number) {
        var parts = x.toString().split(".");
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        return parts.join(".");
    }
    private extractUserId(ctx: Context) {
        const telegramId =
            'message' in ctx.update && typeof (ctx.update.message.from.id) === 'number'
                ? ctx.update.message.from.id
                : 'callback_query' in ctx.update
                    ? ctx.update.callback_query.from.id
                    : null;
        return telegramId;
    }
    private extractText(ctx: Context) {
        const messageText = 'message' in ctx.update && 'text' in ctx.update.message ? ctx.update.message.text : null
        return messageText
    }
    private extractMessageId(ctx: Context) {
        const messageId = 'message' in ctx.update ? ctx.update.message.message_id : null
        return messageId
    }
    async isUserInGroup(chatId: string | number, userId: number) {
        const TELEGRAM_API_URL = 'https://api.telegram.org';
        const BOT_TOKEN = this.configService.get('TELEGRAM_BOT_TOKEN')
        const endpoint = `${TELEGRAM_API_URL}/bot${BOT_TOKEN}/getChatMember?chat_id=${chatId}&user_id=${userId}`;
        try {
            const response = await axios.get(endpoint);
            const status = response.data.result.status;
            return status !== 'left' && status !== 'kicked';
        } catch (error) {
            return false;
        }
    }
    private async sendAIAgentResponse(ctx: Context) {
        const aiAgentResponse = await axios.post(this.aiAgentURL, { payload: ctx.update },{
        headers:{
            'Authorization': `Bearer ${this.configService.get('STEAMSHIP_API_KEY')}`
        }
        })
        await ctx.reply(aiAgentResponse.data, {
            parse_mode: 'Markdown',
            disable_web_page_preview: true,
            reply_to_message_id: this.extractMessageId(ctx)
        });
    }
 
}