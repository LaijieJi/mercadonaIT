import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { type ServerResponse } from './models';
import {
  Camera,
  ChefHat,
  LoaderCircle,
  LucideAngularModule,
  Sparkles,
} from 'lucide-angular';

const exampleData: ServerResponse = {
  name: 'Spaghetti Carbonara',
  recipe: [
    'Boil spaghetti in salted water until al dente.',
    'In a separate pan, cook pancetta until crispy.',
    'In a bowl, whisk together eggs and cheese.',
    'Drain spaghetti and add to pancetta pan.',
    'Remove from heat and quickly mix in egg and cheese mixture.',
    'Serve immediately with extra cheese and pepper.',
  ],
  ingredients: [
    {
      name: 'Spaghetti',
      img_url:
        'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2kbsX1IbOLCT4bVs_rFueXiXrdiBMMDhbEw&s',
      price: 1.5,
    },
    {
      name: 'Pancetta',
      img_url: 'https://m.media-amazon.com/images/I/71goicKgmSL.jpg',
      price: 3.0,
    },
    {
      name: 'Eggs',
      img_url:
        'https://bakerpedia.com/wp-content/uploads/2020/03/Egg_baking-ingredients-e1584136402126.jpg',
      price: 0.2,
    },
    {
      name: 'Parmesan Cheese',
      img_url:
        'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Parmigiano_Reggiano%2C_Italien%2C_Europ%C3%A4ische_Union.jpg/960px-Parmigiano_Reggiano%2C_Italien%2C_Europ%C3%A4ische_Union.jpg',
      price: 2.5,
    },
  ],
};

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, LucideAngularModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'mercadona-chef';

  imageSrc: string | ArrayBuffer | null = null;
  isSubmitting = false;
  response: ServerResponse | null = null;

  readonly Camera = Camera;
  readonly Sparkles = Sparkles;
  readonly ChefHat = ChefHat;
  readonly LoaderCircle = LoaderCircle;
  
  adjustTextareaHeight(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imageSrc = e.target?.result || null;
      };
      reader.readAsDataURL(input.files[0]);
    }
  }
  async onSubmit(): Promise<void> {
    if (this.imageSrc) {
      this.isSubmitting = true;
      const formData = new FormData();
      const blob = this.dataURLToBlob(this.imageSrc);
      formData.append('image', blob, 'uploaded-image.png');

      try {
        const response = await fetch('http://localhost:8000', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to upload image');
        }

        const data = await response.json();
        console.log('Image uploaded successfully:');
        console.log('Name:', data.name);
        console.log('Recipe:', data.recipe);
        console.log('Ingredients:', data.ingredients);

        this.response = data;
      } catch (error) {
        console.error('Error uploading image:', error);
        this.response = exampleData;
      } finally {
        this.isSubmitting = false;
      }
    } else {
      console.error('No image selected to upload.');
    }
  }

  private dataURLToBlob(dataURL: string | ArrayBuffer): Blob {
    const byteString = atob((dataURL as string).split(',')[1]);
    const mimeString = (dataURL as string)
      .split(',')[0]
      .split(':')[1]
      .split(';')[0];
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const uint8Array = new Uint8Array(arrayBuffer);

    for (let i = 0; i < byteString.length; i++) {
      uint8Array[i] = byteString.charCodeAt(i);
    }

    return new Blob([arrayBuffer], { type: mimeString });
  }
}
