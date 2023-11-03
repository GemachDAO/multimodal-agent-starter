import { Module } from '@nestjs/common';
import { TelegrafModule } from 'nestjs-telegraf';
import { ConfigModule, ConfigService } from '@nestjs/config';
import {TelegramUpdate} from './telegram.update'
import { UsersService } from 'src/users/users.service';
import { UsersRepository } from 'src/users/users.repository';
import { UsersModule } from 'src/users/users.module';
import { MongooseModule } from '@nestjs/mongoose';
import { User, UserSchema } from 'src/users/schemas/user.schema';
@Module({
  imports: [
    MongooseModule.forFeature([{name:User.name,schema:UserSchema}]),
    TelegrafModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (configService: ConfigService) => ({
        token: configService.get<string>('TELEGRAM_BOT_TOKEN'),
      }),
      inject: [ConfigService]
    }),
    UsersModule
  ],
  providers: [TelegramUpdate,UsersService,UsersRepository,ConfigService],
  exports:[TelegramUpdate,UsersService,UsersRepository,ConfigService]
})
export class TelegramModule { }
