import { Injectable } from "@nestjs/common";
import { User } from "./schemas/user.schema";
import { UsersRepository } from "./users.repository";
@Injectable()
export class UsersService {
    constructor(private readonly userepository: UsersRepository) { }
    async getUsers(): Promise<User[]> {
        return this.userepository.find({})
    }
    async getUser(telegramId:number): Promise<User> {
        return this.userepository.findOne({telegramId})
    }
}