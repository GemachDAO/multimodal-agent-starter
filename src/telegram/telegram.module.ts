import { Module } from '@nestjs/common';
import { TelegrafModule } from 'nestjs-telegraf';
import { ConfigModule, ConfigService } from '@nestjs/config';
import {TelegramUpdate} from './telegram.update'
@Module({
  imports: [
    TelegrafModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (configService: ConfigService) => ({
        token: configService.get<string>('TELEGRAM_BOT_TOKEN'),
      }),
      inject: [ConfigService]
    }),
  ],
  providers: [TelegramUpdate,ConfigService],
  exports:[TelegramUpdate,ConfigService]
})
export class TelegramModule { }
