import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { TelegramModule } from './telegram/telegram.module';
import { TelegrafModule } from 'nestjs-telegraf';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { MongooseModule } from '@nestjs/mongoose';
import { UsersModule } from './users/users.module';
const configService = new ConfigService();
@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    TelegramModule,
    MongooseModule.forRoot(configService.get('MONGO_URI')),
    UsersModule
    // MongooseModule.forRoot(configService.get('MONGO_URI'))
  ],
  controllers: [AppController],
  providers: [AppService],
  // TelegrafModule.
})
export class AppModule { }
