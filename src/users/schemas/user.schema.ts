
import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import {Document } from 'mongoose';
export type UserDocument =User & Document
@Schema({
    autoIndex: true,
    timestamps: true,
    collection: 'users',
})
export class User{
    @Prop({ required: false, lowercase: true, type: String })
    userAddress: string;
    @Prop({ required: true, type: String })
    username: string;
    @Prop({ required: false, lowercase: true, type: Number, default: null })
    telegramId: number | null;
    @Prop({ type: Boolean, default: false })
    isFreeUser: boolean;
}
export const UserSchema = SchemaFactory.createForClass(User);
