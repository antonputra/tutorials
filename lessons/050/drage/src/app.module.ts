import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { MongooseModule } from '@nestjs/mongoose';
import { BooksModule } from './books/books.module';


const username = process.env.MONGODB_USERNAME;
const password = process.env.MONGODB_PASSWORD;
const dbHost = process.env.MONGODB_HOSTNAME;
const port = process.env.MONGODB_PORT;
const database = process.env.MONGODB_DATABASE;

const connectionString = `mongodb://${dbHost}:${port}/${database}`;

const options = {
  user: username,
  pass: password
};

@Module({
  imports: [MongooseModule.forRoot(connectionString, options), BooksModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
