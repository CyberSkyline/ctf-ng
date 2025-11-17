import fs from 'fs';
import handlebars from 'handlebars';
import { convert as htmlToText } from 'html-to-text';
import mjml from 'mjml';
import path from 'path';

const __dirname = import.meta.dirname;

export default class Template {
  constructor({ name, subject, file }) {
    const fullFilepath = path.join(__dirname, 'templates', file);
    if (!fs.existsSync(fullFilepath)) throw new Error(`Template file not found: ${fullFilepath}`);
    if (!name) throw new Error('Template name is required');
    if (!subject) throw new Error('Template subject is required');

    this.name = name;
    this.subject = subject;
    this.filePath = fullFilepath;
    this.template = fs.readFileSync(this.filePath, 'utf8');
  }

  render(args = {}) {
    // Compile and render the Handlebars template
    const compiledTemplate = handlebars.compile(this.template);
    const renderedMjml = compiledTemplate(args);
    
    // Convert MJML to HTML
    const mjmlResult = mjml(renderedMjml, {
      keepComments: false,
      beautify: false,
    });
    
    if (mjmlResult.errors.length > 0) {
      console.warn('MJML conversion warnings:', mjmlResult.errors);
    }
    
    const html = mjmlResult.html;
    
    // Create plain text version
    const text = htmlToText(html, {
      wordwrap: 80,
      preserveNewlines: true,
      uppercaseHeadings: false,
      hideLinkHrefIfSameAsText: true,
      ignoreHref: false,
      ignoreImage: true,
      tables: true,
      unorderedListItemPrefix: '• ',
      orderedListItemPrefix: function(o, level, prefix) {
        return prefix + '. ';
      }
    });
    
    return { html, text };
  }
}

