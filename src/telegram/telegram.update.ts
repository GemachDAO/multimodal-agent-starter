import {
    Update,
    Ctx,
    Start,
    Help,
    On,
} from 'nestjs-telegraf';
import { Context } from 'telegraf';
import axios from 'axios'
import { UsersService } from 'src/users/users.service';
import { ConfigService } from '@nestjs/config';
@Update()
export class TelegramUpdate {
    private aiAgentURL: string
    constructor(private readonly userService: UsersService, private readonly configService: ConfigService) {
        this.aiAgentURL = configService.get('AI_AGENT_URL')
    }
    @Start()
    async start(@Ctx() ctx: Context) {
        const userId = this.extractUserId(ctx)
        const user = await this.userService.getUser(userId)
        let updatedCtx = null
        if (!user || !user.isFreeUser) {
            updatedCtx = this.updatePrompt(ctx)
            await this.sendAIAgentResponse(updatedCtx)
        } else {
            this.sendAIAgentResponse(ctx)
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

    @On('sticker')
    async on(@Ctx() ctx: Context) {
        await ctx.reply(`😄 Looks like you sent a sticker! While I can't visually appreciate it, I'm here to help with any DeFi insights or questions you might have. Let's dive into the DeFi universe together! 🌌
        `);
    }
    @On('text')
    async handleTextResponses(@Ctx() ctx: Context) {
        await this.sendAIAgentResponse(ctx)

    }


    private extractUserId(ctx: Context) {
        const telegramId =
            'message' in ctx.update && typeof (ctx.update.message.from.id) === 'number'
                ? ctx.update.message.from.id
                : 'callback_query' in ctx.update
                    ? ctx.update.callback_query.from.id
                    : null;

        const username =
            'message' in ctx.update && typeof (ctx.update.message.from.id) === 'number'
                ? ctx.update.message.from.username || ctx.update.message.from.first_name
                : 'callback_query' in ctx.update
                    ? ctx.update.callback_query.from.username ||
                    ctx.update.callback_query.from.first_name
                    : null;
        return telegramId;
    }
    private updatePrompt(ctx: Context) {
        'message' in ctx.update ? 'text' in ctx.update.message ? ctx.update.message.text = `${ctx.update.message.text} not a member` : null : null;
        return ctx
    }
    private async sendAIAgentResponse(ctx: Context) {
        const aiAgentResponse = await axios.post(this.aiAgentURL, { payload: ctx.update })
        console.log(aiAgentResponse.data);
        await ctx.reply(aiAgentResponse.data.data, {
            parse_mode: 'Markdown',
            disable_web_page_preview: true
        });
    }
}